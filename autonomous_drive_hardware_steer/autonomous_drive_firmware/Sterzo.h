#ifndef STERZO_H
#define STERZO_H

#include <Arduino.h>
#include <Servo.h>

class Sterzo {
private:
    Servo servo;
    int minLeft;
    int center;
    int maxRight;

public:
    Sterzo(int minLeft = 60, int center = 90, int maxRight = 120);
    void attach(int pin);
    void set(int relativePos);

    // 👇 Public getters for steering limits
    int getMinLeft() const { return minLeft; }
    int getCenter() const { return center; }
    int getMaxRight() const { return maxRight; }
};

#endif
