#include "Sterzo.h"

Sterzo::Sterzo(int minLeft, int center, int maxRight)
  : minLeft(minLeft), center(center), maxRight(maxRight) {}

void Sterzo::attach(int pin) {
    servo.attach(pin);
    servo.write(center); // start centered
}

void Sterzo::set(int relativePos) {
    int target = center + relativePos;

    // Clamp limits
    if (target < minLeft)  target = minLeft;
    if (target > maxRight) target = maxRight;

    servo.write(target);
}
