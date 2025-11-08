// ─────────────────────────────────────────────
//                Motor.h
// ─────────────────────────────────────────────
#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
public:
  // ─────────────── Constructor ───────────────
  Motor(uint8_t pinRPWM, uint8_t pinLPWM);

  // ─────────────── Setup ───────────────
  void begin();

  // ─────────────── Motion control ───────────────
  void Forward(int pwm);   // move forward
  void Backward(int pwm);  // move backward
  void Stop();             // stop both pins

private:
  uint8_t _pinRPWM;
  uint8_t _pinLPWM;
};

#endif
