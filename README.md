# mac-plus-serkey
Arduino code and Pygame host for a Macintosh (non-ADB) keyboard

The code in this project is based on Tomek Rekawek's `mac-plus-ps2`
project, which interfaces a PS/2 keyboard to the Mac through an
Arduino. It is probably less laggy and more reliable than my code,
which uses some functions from `mac-plus-ps2`.

This project emulates a Macintosh 128K-to-Plus-compatible keyboard
using any Serial-capable Arduino. It is a PlatformIO project,
configured for the "metro" target (so it should run on any
Uno-compatible board). Usage is simple: connect a keyboard cable,
upload the sketch, and run the host Python script.

## Keyboard connections
These can be changed with the `#define`s at the top of
`src/mac-plus-serkey.cxx`. The defaults are as follows:

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
Connect the Arduino and the Mac together in any order. The order
doesn't matter, as the Arduino will "synchronize" (it's a very basic
protocol) with the Mac. The script uses
[pyserial](https://pythonhosted.org/pyserial/) and
[pygame](https://www.pygame.org/), so make sure those are
installed. Then, run the `pygame_host.py` script with the serial port
as the first argument. For example, assuming `python` is Python 3:

```$ python pygame_host.py /dev/ttyUSB0```

The window that appears is the keyboard window, so only keys pressed
while that window is active will be sent to the Arduino.

I have no idea if this works under any OS besides Linux, but it
probably does.
