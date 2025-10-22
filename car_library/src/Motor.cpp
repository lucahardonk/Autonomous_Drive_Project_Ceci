// ─────────────────────────────────────────────
//                Motor.cpp
// ─────────────────────────────────────────────
#include "Motor.h"

// ─────────────── Constructor ───────────────
Motor::Motor(uint8_t pinRPWM, uint8_t pinLPWM)
  : _pinRPWM(pinRPWM), _pinLPWM(pinLPWM) {}

// ─────────────── begin() ───────────────
void Motor::begin() {
  pinMode(_pinRPWM, OUTPUT);
  pinMode(_pinLPWM, OUTPUT);

  Stop();
}

// ─────────────── Stop ───────────────
void Motor::Stop() {
  analogWrite(_pinRPWM, 0);
  analogWrite(_pinLPWM, 0);
}

// ─────────────── Forward ───────────────
void Motor::Forward(int pwm) {
  pwm = constrain(pwm, 0, 255);
  analogWrite(_pinRPWM, pwm);
  analogWrite(_pinLPWM, 0);
}

// ─────────────── Backward ───────────────
void Motor::Backward(int pwm) {
  pwm = constrain(pwm, 0, 255);
  analogWrite(_pinRPWM, 0);
  analogWrite(_pinLPWM, pwm);
}
