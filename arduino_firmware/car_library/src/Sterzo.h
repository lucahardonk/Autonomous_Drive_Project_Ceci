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
    // ─────────────── Constructors ───────────────
    Sterzo(int minLeft = 30, int center = 60, int maxRight = 90);

    // ─────────────── Setup ───────────────
    void attach(int pin);

    // ─────────────── Control ───────────────
    void set(int relativePos);

    // ─────────────── Getters ───────────────
    int getMinLeft() const { return minLeft; }
    int getCenter() const { return center; }
    int getMaxRight() const { return maxRight; }

    // ─────────────── Setters ───────────────
    void setMinLeft(int value) { minLeft = value; }
    void setCenter(int value) { center = value; }
    void setMaxRight(int value) { maxRight = value; }
};

#endif
