#ifndef ENCODER_H
#define ENCODER_H

#include <Arduino.h>

class Encoder {
public:
  Encoder(uint8_t pinA, uint8_t pinB, int cpr)
      : pinA(pinA), pinB(pinB), CPR(cpr), position(0), lastState(0) {}

  void begin();
  void update();
  void printState();

private:
  uint8_t pinA, pinB;
  int CPR;
  volatile long position;
  uint8_t lastState;

  // Two static instances (supports two encoders)
  static Encoder* encoder0;
  static Encoder* encoder1;

  static void handleInterruptA();
  static void handleInterruptB();
};

#endif
