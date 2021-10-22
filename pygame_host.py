import pygame

import serial
import sys
# Data from Inside Macintosh Volume IV (for a Macintosh Plus)

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
    # we have to do this because there's no
    # .lower() equivalent for shifted numbers

    # note that these are the same as the unshifted,
    # because the Shift handling is done by the Mac
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
    pygame.K_CAPSLOCK: 0x6f, # Command, though I could also make this be Option
    pygame.K_LCTRL: 0x75, # Option
    pygame.K_RCTRL: 0x75, # Option
    pygame.K_LALT: 0x6f, # Command
    pygame.K_RALT: 0x69, # Enter
    pygame.K_TAB: 0x61,

    # I think this does something different, because
    # these numbers are also numbers for letters

    # These would have to send the Keypad response ($79) back and then
    # send the keycode.

    # arrow keys, these don't work right
    pygame.K_LEFT: 0x0d,
    pygame.K_RIGHT: 0x05,
    pygame.K_UP: 0x1b,
    pygame.K_DOWN: 0x11
    
}

# key is the pygame key pressed
# transition is True for pressed, False for released.
def generate_keycode(key: int, transition: bool):
    print('key', key, 'transition', transition)

    keycode = keycodes[key]
    if transition:
        keycode |= 0b10000000

    return keycode
    



ser = serial.Serial(sys.argv[1], 230400)
# the display package handles keypresses; initing just it keeps the
# CPU usage very low (whereas before it was 100% all the time).
pygame.display.init()
pygame.mixer.quit()
pygame.display.set_mode((320, 240))
# make the window black so it doesn't pick up crud in video memory
pygame.display.flip()
import time
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            code = generate_keycode(event.key, False).to_bytes(1, 'little')
            #if event.key == pygame.K_LEFT:
            #    print('left arrow keydown')
            #    ser.write(0x79)
            #    ser.write(code)
            #else:
            ser.write(code)
        elif event.type == pygame.KEYUP:
            code = generate_keycode(event.key, True).to_bytes(1, 'little')
            # arrow keys should be handled by a special thing on the arduino side
            
            #if event.key == pygame.K_LEFT:
            #    print('left arrow keyup')
            #    ser.write(0x79)
            #    ser.write(code)
            #else:
            ser.write(code)
    time.sleep(0.1) # seems to help reduce CPU usage
