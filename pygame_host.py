# At least on Linux, this suppresses Pygame's welcome message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import serial
import time
import sys
import argparse

# This script works reasonably simply: if a non-keypad key changes
# state (i.e., is pressed or released) on the computer while the
# Pygame window is active, the script sends the corresponding keycode
# to the Arduino. The script will send the exact byte that the Arduino
# needs to send to the Mac, to reduce latency. Each key is stored in
# the dictionary as the key-down version, and is ORed with 0x80
# (0b10000000) when the key is released. This is to match the
# key-up/key-down scheme documented in Inside Macintosh.

# Keypad keys work a little differently. They use special codes that
# don't map to any keyboard key. The Arduino recognizes these special
# codes and follows the Keypad protocol (see Inside Macintosh Vol. III
# for details), eventually sending the correct key for what was
# pressed or released on the computer.

# Data from Inside Macintosh Volumes III & IV
keycodes = {
    pygame.K_a: 0x01,
    pygame.K_s: 0x03,
    pygame.K_d: 0x05,
    pygame.K_f: 0x07,
    pygame.K_g: 0x0b,
    pygame.K_h: 0x09,
    pygame.K_j: 0x4d,
    pygame.K_k: 0x51,
    pygame.K_l: 0x4b,
    pygame.K_SEMICOLON: 0x53,
    pygame.K_QUOTE: 0x4f,

    # top row
    pygame.K_q: 0x19,
    pygame.K_w: 0x1b,
    pygame.K_e: 0x1d,
    pygame.K_r: 0x1f,
    pygame.K_t: 0x23, 
    pygame.K_y: 0x21,
    pygame.K_u: 0x41,
    pygame.K_i: 0x45,
    pygame.K_o: 0x3f, 
    pygame.K_p: 0x47,
    pygame.K_LEFTBRACKET: 0x43,
    pygame.K_RIGHTBRACKET: 0x3d,
    pygame.K_BACKSLASH: 0x55,

    # bottom row
    pygame.K_z: 0x0d,
    pygame.K_x: 0x0f,
    pygame.K_c: 0x11,
    pygame.K_v: 0x13,
    pygame.K_b: 0x17,
    pygame.K_n: 0x5b,
    pygame.K_m: 0x5d,
    pygame.K_COMMA: 0x57,
    pygame.K_PERIOD: 0x5f,
    pygame.K_SLASH: 0x59, 

    # number row
    pygame.K_BACKQUOTE: 0x65,
    pygame.K_1: 0x25,
    pygame.K_2: 0x27,
    pygame.K_3: 0x29,
    pygame.K_4: 0x2b,
    pygame.K_5: 0x2f,
    pygame.K_6: 0x2d,
    pygame.K_7: 0x35,
    pygame.K_8: 0x39,
    pygame.K_9: 0x33,
    pygame.K_0: 0x3b,
    pygame.K_MINUS: 0x37,
    pygame.K_EQUALS: 0x31,

    # shifted number row
    
    # we have to include this because there's no Python str.lower()
    # equivalent for shifted numbers

    # note that these are the same as the unshifted, because the Shift
    # handling is done by the Mac
    pygame.K_BACKQUOTE: 0x65,
    pygame.K_EXCLAIM: 0x25,
    pygame.K_AT: 0x27,
    pygame.K_HASH: 0x29,
    pygame.K_DOLLAR: 0x2b,
    pygame.K_PERCENT: 0x2f,
    pygame.K_CARET: 0x2d,
    pygame.K_AMPERSAND: 0x35,
    pygame.K_ASTERISK: 0x39,
    pygame.K_LEFTPAREN: 0x33,
    pygame.K_RIGHTPAREN: 0x3b,
    pygame.K_LEFTBRACKET: 0x43, 
    pygame.K_RIGHTBRACKET: 0x3D,

    pygame.K_SPACE: 0x63,
    pygame.K_BACKSPACE: 0x67,
    pygame.K_LSHIFT: 0x71,
    pygame.K_RSHIFT: 0x71,
    pygame.K_RETURN: 0x49,
    pygame.K_CAPSLOCK: 0x73,
    pygame.K_LCTRL: 0x75, # Option
    pygame.K_RCTRL: 0x75, # Option
    pygame.K_LALT: 0x6f, # Command
    pygame.K_RALT: 0x6f, # Command
    pygame.K_TAB: 0x61,

    # keypad codes

    # to follow with the same bit 7 scheme as the other keycodes,
    # these are 0xFF, 0xFE, 0xFD, and 0xFC but bit 7 has been set low
    # for each of those four numbers
    pygame.K_LEFT: 0x7f, 
    pygame.K_RIGHT: 0x7e, 
    pygame.K_UP: 0x7d, 
    pygame.K_DOWN: 0x7c,

    # we have learned from experience that some applications (MPW in
    # particular) need the Enter key. We'll map it to Keypad enter,
    # but also to the Delete key, since not everyone has a numpad on
    # their keyboard.
    pygame.K_DELETE: 0x69,
    pygame.K_KP_ENTER: 0x69
}


class PygameHost(object):
    def __init__(self, port: str, capslock_reassigned: bool):
        self.capslock_reassigned = capslock_reassigned
        self.ser = serial.Serial(port, 230400)
        # we only initialize the packages we need, because I was
        # having issues with this script using 100% CPU for no reason,
        # and this seemed to help stop that.
        pygame.display.init()
        pygame.font.init()
        # Kill the mixer in particular. On Linux, this is known to
        # cause issues because of some odd interactions with ALSA.
        pygame.mixer.quit()

        # A much more useful image would be one that shows what each
        # key on a modern keyboard (which I think we can assume is
        # basically the same regardless of computer) maps to
        keyboardImage = pygame.image.load('mac_plus_lkbd.jpg')
        # The image is 974x473, so let's make it half size in a window of the
        # same size, which is 487x237
        dimensions = (
            (int)(keyboardImage.get_width() / 2),
            (int)(keyboardImage.get_height() / 2)
        )
        keyboardImage = pygame.transform.scale(keyboardImage, dimensions)

        # the image is from Herb's Mac Stuff:
        # http://retrotechnology.com/herbs_stuff/mac_plus_lkbd.jpg
        self.disp = pygame.display.set_mode(dimensions)
        pygame.display.set_caption('Mac Plus serial keyboard: Caps Lock off')
        self.disp.blit(keyboardImage, (0, 0))
        
        font = pygame.font.Font(None, 18)
        # arguments to this function: string, antialiasing toggle, color
        text = font.render(
            'image source: http://retrotechnology.com/herbs_stuff/mac_plus_lkbd.jpg',
            1,
            (255, 255, 255))
        self.disp.blit(text, (45, 216))
        
        pygame.display.update()

    # key is the pygame key pressed
    # transition is True for pressed, False for released.
    def generate_keycode(self, key: int, transition: bool):
        keycode = keycodes[key]
        if transition:
            # if the key has been released, set bit 7
            keycode |= 0b10000000

        return keycode.to_bytes(1, 'little')
    
    def main_loop(self):
        # The Caps Lock key on the real keyboard physically locks, so
        # the keyup code is only sent when Caps Lock is turned
        # off. That means we need a variable here to keep track of the
        # state.
        capslock = False
        # whether or not the last key pressed was Caps Lock
        lastdown = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_CAPSLOCK and not self.capslock_reassigned:
                        if capslock:
                            # this will jump to the outer while True
                            # loop, restarting the event loop
                            break
                        else:
                            # we should have a caps lock status thing
                            # in the window
                            capslock = True
                            lastdown = True
                            pygame.display.set_caption(
                                'Mac Plus serial keyboard: Caps Lock on')

                    # If the key pressed isn't in the dictionary, a
                    # KeyError is thrown unless we catch it
                    try:
                        code = self.generate_keycode(event.key, False)
                        self.ser.write(code)
                    except KeyError:
                        pass
                elif event.type == pygame.KEYUP:
                    # if the key is Caps Lock, we should only send the
                    # keyup code when capslock is true
                    if event.key == pygame.K_CAPSLOCK and not self.capslock_reassigned:
                        if capslock and not lastdown:
                            capslock = False
                            pygame.display.set_caption(
                                'Mac Plus serial keyboard: Caps Lock off')
                        else:
                            lastdown = False
                            break

                    try:
                        code = self.generate_keycode(event.key, True)
                        self.ser.write(code)
                    except KeyError:
                        pass
            # This time.sleep() also seems to reduce CPU usage
            time.sleep(0.1)
            # if we don't call update(), the window will pick up
            # odd artifacts from video memory and look bad.
            pygame.display.update()


if __name__ == '__main__':
    # There are two arguments for convienence: --caps-is-option,
    # --caps-is-command
    
    # all they do is set the pygame.K_CAPSLOCK key to either the
    # Option keycode or the Command keycode

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'port',
        help='The serial port to send key presses and releases to')

    # Caps Lock can only be Caps Lock, Option, or Command: these two
    # options are mutually exclusive
    caps_group = parser.add_mutually_exclusive_group()
    caps_group.add_argument(
        '-o',
        '--caps-is-option',
        action='store_true',
        help="Send the Option key when the host's Caps Lock key is pressed")
    caps_group.add_argument(
        '-c',
        '--caps-is-command',
        action='store_true',
        help="Send the Command key when the host's Command key is pressed")

    args = parser.parse_args()

    capslock_reassigned = False
    if args.caps_is_option:
        print('Caps Lock has been reassigned to Option')
        # reassign the pygame.K_CAPSLOCK keycode to the pygame.K_OPTION keycode
        keycodes[pygame.K_CAPSLOCK] = keycodes[pygame.K_LCTRL]
        capslock_reassigned = True
    elif args.caps_is_command:
        print('Caps Lock has been reassigned to Command')
        keycodes[pygame.K_CAPSLOCK] = keycodes[pygame.K_LALT]
        capslock_reassigned = True
    host = PygameHost(args.port, capslock_reassigned)
    host.main_loop()
