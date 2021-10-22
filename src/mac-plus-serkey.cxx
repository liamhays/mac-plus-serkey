// Adapted from https://github.com/trekawek/mac-plus-ps2.

// The author used the resources, apparently.
// Guide 1: http://www.synack.net/~bbraun/mackbd/index.html
// Guide 2: http://www.mac.linux-m68k.org/devel/plushw.php

// Mac keycodes are defined in Inside Macintosh, Volume III.
#include <Arduino.h>

// In the cable I made, the colors of the SOLID-CORE wires map to
// these signals:
// | Green  | GND   |
// | Red    | Clock | ardu pin 2
// | White  | Data  | ardu pin 3
// | Yellow | +5V   |

// This code works, but it's laggy and likes to frequently repeat
// characters even though I never pressed the key multiple times or
// held it down. I believe it is printing out either 8 or 9 characters
// total when it decides to repeat.
#define MAC_CLOCK_PIN 2
#define MAC_DATA_PIN 3

#define NULL_KEYCODE 0x7b

// The 4 kinds of commands that the Mac can send
#define CMD_INQUIRY 0x10
#define CMD_INSTANT 0x14
#define CMD_MODEL_NUMBER 0x16
#define CMD_TEST 0x36

#define LED_SEND 6
#define LED_RECEIVE 7

byte readCmd();
void inquiry();
byte readByte();
void sendByte(byte b);


void setup() {
  // let's use a real fast baud rate for minimal latency
  // at the amount I'll be typing, 115200 is probably sufficient.
  Serial.begin(230400);
  
  pinMode(LED_SEND, OUTPUT);
  pinMode(LED_RECEIVE, OUTPUT);

  // The keyboard is responsible for creating a clock signal, which
  // varies depending on what is going on.
  pinMode(MAC_CLOCK_PIN, OUTPUT);
  pinMode(MAC_DATA_PIN, INPUT_PULLUP);
}

void loop() {
  pinMode(MAC_DATA_PIN, INPUT_PULLUP);
  // Wait for the Mac to pull the data low, which signals that it is
  // going to send a command.
  while (digitalRead(MAC_DATA_PIN) != LOW); /* {
    Serial.println("waiting for Mac data to go low");
    }*/

  // This delay is from Guide 1, which says that the clock must be
  // delayed a little bit from the moment the data pin falls, so that
  // the computer won't miss it.

  // 400 µs is probably too long, as Guide 1 says that 180 µs is
  // sufficient. However, it's the work of the original author, and it
  // will stay until I can test it.
  delayMicroseconds(400);
  

  byte cmd = readByte();
  // The Mac indicates that it's ready for a response by driving the
  // data high.
  while (digitalRead(MAC_DATA_PIN) != HIGH);
  Serial.println("Mac data is high");
  byte serData;
  switch (cmd) {
  case CMD_INQUIRY:
    inquiry();
    break;
    
  case CMD_INSTANT:
    // The Instant command is quite boring: the keyboard just
    // responds with its status without any of the 250 ms timeout
    // like in Inquiry.

    serData = Serial.read();
    if (serData != -1) {
      sendByte(serData);
    } else {
      sendByte(NULL_KEYCODE);
    }
    break;

  case CMD_MODEL_NUMBER:
    // 0x03 is just "keyboard, model 1, no peripherals". This is a
    // generic response since the Mac expects /something/.
    sendByte(0b00000101); // keyboard model 2, maybe Mac Plus?
    break;
    
  case CMD_TEST:
    // Send ACK, simply because we have no way to test. NAK is 0x77.
    sendByte(0x7d);
    break;
  }
}

void inquiry() {
  pinMode(MAC_DATA_PIN, OUTPUT);
  // Inquiry begins a timer on the keyboard: if no key is pressed in
  // 250 ms (not µs), then the keyboard will send back the null key
  // transition code, NULL_KEYCODE. If the Mac doesn't get any
  // response after 500 ms, it will send the Model Number command to
  // try to reset the keyboard.

  unsigned long start = millis();
  // This needs to do something different, so that if the timeout
  // occurs, no Serial.read() result is sent.
  // That said, it works...I don't know why.
  
  int key = Serial.read();
  while ((millis() - start) < 250 && key == -1) {
    key = Serial.read();
  }
  // now either key is not -1 or the timeout has occurred
  // obviously each happening must be handled separately
  if (key == -1) {
    sendByte(NULL_KEYCODE);
  } else {
    Serial.print("sent a key");
    sendByte(key);
  }
}

byte readByte() {
  digitalWrite(LED_RECEIVE, HIGH);
  // During a read, the keyboard is responsible for clocking. It
  // follows the 180/220 µs (400 µs cycle) clocking scheme in read.
  byte b = 0;
  for (byte i = 0; i < 8; i++) {
    digitalWrite(MAC_CLOCK_PIN, LOW);
    delayMicroseconds(180);
    digitalWrite(MAC_CLOCK_PIN, HIGH);
    // Note that we don't delay 220 µs here, because the keyboard must
    // read the Mac's sent data 80 µs after the rising edge of the
    // clock. The rest of the delay comes later
    delayMicroseconds(80);
    // The data the Mac sends is lowest bit first.
    b = (b << 1) | digitalRead(MAC_DATA_PIN);
    // Why doesn't digitalRead() take enough time that this should be
    // less than 140?
    delayMicroseconds(140);
  }
  digitalWrite(LED_RECEIVE, LOW);
  return b;
}

void sendByte(byte b) {
  digitalWrite(LED_SEND, HIGH);
  // Again, the keyboard is still responsible for clocking, but using
  // the 330 µs scheme this time.

  // This is a super weird, but rather genius, way to send the data. m
  // is shifted right by one each loop, creating a bitmask that
  // reveals only one bit each loop, starting at the highest bit.
  for (byte m = 128; m > 0; m >>= 1) {
    // Write the bit 40 µs /before/ the clock goes low, as per the
    // protocol standard. It is held through the entire cycle.
    digitalWrite(MAC_DATA_PIN, (b & m) ? HIGH : LOW);
    delayMicroseconds(40);
    // The clock then goes low for 120 µs.
    digitalWrite(MAC_CLOCK_PIN, LOW);
    delayMicroseconds(120);
    // Then it rises for 170 µs. The Mac reads the bit on this rising
    // edge.
    digitalWrite(MAC_CLOCK_PIN, HIGH);
    delayMicroseconds(170);
  }
  digitalWrite(LED_SEND, LOW);
  // Return control to the Mac.
  digitalWrite(MAC_DATA_PIN, HIGH);
}

