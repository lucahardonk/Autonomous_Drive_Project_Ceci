#include "Car.h"

Car::Car()
: leftEncoder(2, 3, 411),
  rightEncoder(12, 8, 411),
  leftMotor(5, 6),
  rightMotor(9, 10),
  steering()  // uses default minLeft/center/maxRight
{
}

void Car::begin() {
  leftEncoder.begin();
  rightEncoder.begin();
  leftMotor.begin();
  rightMotor.begin();
  steering.attach(steeringPin);
  steering.set(0); // center steering
}

void Car::drive(int speedLeft, int speedRight, int direction) {
  if (direction > 0) {
    leftMotor.Forward(speedLeft);
    rightMotor.Forward(speedRight);
  } else if (direction < 0) {
    leftMotor.Backward(speedLeft);
    rightMotor.Backward(speedRight);
  } else {
    stop();
  }
}

void Car::stop() {
  leftMotor.Stop();
  rightMotor.Stop();
}

void Car::steer(int relativePos) {
  steering.set(relativePos);
}

// ─────────────── Encoder feedback ───────────────
long Car::getLeftEncoderCount() {
  leftEncoder.update();
  return leftEncoder.getCount();
}

long Car::getRightEncoderCount() {
  rightEncoder.update();
  return rightEncoder.getCount();
}

void Car::resetEncoders() {
  leftEncoder.reset();
  rightEncoder.reset();
}


float Car::getLeftEncoderVelocity() {
  return leftEncoder.getVelocity();
}

float Car::getRightEncoderVelocity() {
  return rightEncoder.getVelocity();
}
