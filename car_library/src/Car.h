#ifndef CAR_H
#define CAR_H

#include "Encoder.h"
#include "Motor.h"
#include "Sterzo.h"

class Car {
public:
  Car();
  void begin();

  // ─────────────── Motion control ───────────────
  void drive(int speedLeft, int speedRight, int direction);
  void stop();
  void steer(int relativePos);

  // ─────────────── Encoder feedback ───────────────
  long getLeftEncoderCount();
  long getRightEncoderCount();
  float getLeftEncoderVelocity();   
  float getRightEncoderVelocity();
  void resetEncoders();


  Encoder leftEncoder;
  Encoder rightEncoder;
  Motor leftMotor;
  Motor rightMotor;
  Sterzo steering;


  const int steeringPin = 11;
};

#endif
