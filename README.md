# mac-plus-serkey
Arduino code and Pygame host for a Macintosh (non-ADB) keyboard

This project emulates a Macintosh Plus-compatible keyboard using any
Serial-capable Arduino. It won't replace an original keyboard, but it
should suffice for most basic purposes. It emulates every feature of
the original keyboard, including the arrow keys but excluding the keypad.

Some code in this project is based on Tomek Rekawek's
[`mac-plus-ps2`](https://github.com/trekawek/mac-plus-ps2) project,
which interfaces a PS/2 keyboard to the Mac through an Arduino. It is
probably less laggy and more reliable than my code, which uses some
functions from `mac-plus-ps2`.

The root directory of the repository is a PlatformIO project,
configured for the `metro` target, so it should run on any
Uno-compatible board without change. You can also change the target in
`platformio.ini` for any other Arduino board. Usage is simple: connect
a keyboard cable, upload the sketch, and run the host Python script.

## Keyboard cable connections
The data and clock Arduino pins can be changed with the `#define`s at
the top of `src/mac-plus-serkey.cxx` if desired. The defaults are as
follows:

| Mac pin | Arduino pin |
|---------|-------------|
| Ground  | Ground      |
| Clock   | Pin 2       |
| Data    | Pin 3       |
| +5V     | unconnected |

The Mac's 5 volt supply stays disconnected for two reasons: one, we
don't want to draw more power from it than needed, and two, the
Arduino will receive USB power from the computer.

## Usage
Connect the Arduino, Mac, and the host computer together in any
order. The order doesn't matter, as the Arduino will "synchronize"
with the Mac and the host script works independent of both.

The script is in Python 3. It depends on
[pyserial](https://pythonhosted.org/pyserial/) and
[pygame](https://www.pygame.org/), so install those before running
it. Then, run the `pygame_host.py` script, which requires one
positional argument: the serial port to send keystrokes to. It must be
run from the command line. For example, assuming `python` is Python 3:

```$ python pygame_host.py /dev/ttyUSB0```

The window that appears is the keyboard window. Only keys pressed
while that window is active will be sent to the Arduino and
subsequently to the Mac.

I have tested the script and entire system on Arch Linux and Windows,
and it worked fine on both. I have not tested it on any variety of macOS.

## Keyboard mappings, extra options
The computer's keyboard is mapped more or less character-for-character
to the Mac Plus keyboard. The variations to fit the Mac keyboard are
as follows:

- Left and right **Ctrl** are **Option**
- Left and right **Alt** are **Command**
- Caps Lock emulates the physical key-locking behavior of the original
  keyboard
- Enter (which is not present on the Mac Plus keyboard except on the
  keypad, but is present on the original Mac keyboard) is mapped to
  both **numpad Enter** and the **Delete** key.
- Subsequently, the Mac's **Return** key is mapped to the computer's
**Enter**.

The current Caps Lock status is visible in the keyboard window's
title.

Caps Lock can also be remapped to one of two other keys with optional
command-line flags:

| Option                   | Operation                  |
|--------------------------|----------------------------|
| `-o`/`--caps-is-option`  | remap Caps Lock to Option  |
| `-c`/`--caps-is-command` | remap Caps Lock to Command |

## Bugs and limitations
This project will never replace the real keyboard. It is generally
laggy and skips keystrokes at high speed. This could probably be
fixed, but I don't know how or even what's causing that.

One particular symptom this project exhibits is that the lag time and
reliability seem to decline the longer the Arduino is plugged in. I
don't know why this is, but it can be resolved by unplugging and
reinserting the Arduino, and restarting the Python host accordingly.
