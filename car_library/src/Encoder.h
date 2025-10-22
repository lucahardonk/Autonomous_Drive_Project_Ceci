#ifndef ENCODER_H
#define ENCODER_H

#include <Arduino.h>

class Encoder {
public:
  Encoder(uint8_t pinA, uint8_t pinB, int cpr)
      : pinA(pinA), pinB(pinB), CPR(cpr), position(0), lastA(0) {}

  void begin();
  long getCount() const { return position; }
  void reset() { noInterrupts(); position = 0; interrupts(); }
  void printState();
  void update();
  float getVelocity();

private:
  uint8_t pinA, pinB;
  int CPR;
  volatile long position;
  volatile uint8_t lastA;

  // ─────────────── New members for velocity estimation ───────────────
  unsigned long lastUpdateTime = 0;  // microseconds of last measurement
  long lastPosition = 0;             // previous encoder count
  float velocity = 0.0;              // last computed angular velocity [rad/s]

  // Static pointers + ISR handlers
  static Encoder* encoder0;
  static Encoder* encoder1;
  static void handleInterruptA();
  static void handleInterruptB();
};

#endif
