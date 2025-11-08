#include "Encoder.h"

// Static member initialization
Encoder* Encoder::encoder0 = nullptr;
Encoder* Encoder::encoder1 = nullptr;

void Encoder::begin() {
  pinMode(pinA, INPUT_PULLUP);
  pinMode(pinB, INPUT_PULLUP);
  lastA = digitalRead(pinA);

  // Assign to first available encoder slot
  if (!encoder0) encoder0 = this;
  else if (!encoder1) encoder1 = this;

  // Attach only one interrupt (Channel A)
  if (encoder0 == this)
    attachInterrupt(digitalPinToInterrupt(pinA), handleInterruptA, CHANGE);
  else if (encoder1 == this)
    attachInterrupt(digitalPinToInterrupt(pinA), handleInterruptB, CHANGE);
}

void Encoder::handleInterruptA() { if (encoder0) encoder0->update(); }
void Encoder::handleInterruptB() { if (encoder1) encoder1->update(); }

void Encoder::update() {
  uint8_t a = digitalRead(pinA);
  uint8_t b = digitalRead(pinB);

  // If A changed:
  if (a != lastA) {
    // Direction depends on the state of B
    if (a == b) position++;
    else        position--;
    lastA = a;
  }
}

void Encoder::printState() {
  noInterrupts();
  long pos = position;
  interrupts();
  Serial.print("Position: ");
  Serial.print(pos);
  Serial.print(" | CPR: ");
  Serial.println(CPR);
}


float Encoder::getVelocity() {
  unsigned long now = micros();

  if (lastUpdateTime == 0) {
    lastUpdateTime = now;
    noInterrupts();
    lastPosition = position;
    interrupts();
    return 0.0f;
  }

  unsigned long dt = now - lastUpdateTime;
  if (dt == 0) return velocity;  // avoid division by zero

  noInterrupts();
  long currentCount = position;
  interrupts();

  long deltaCount = currentCount - lastPosition;
  lastPosition = currentCount;
  lastUpdateTime = now;

  float newVelocity = ( (float)deltaCount * (2.0 * PI) * 1000000) / ( (float)CPR * dt );   // dt in ms → OK

  //newVelocity = newVelocity/4;

  return newVelocity;
}

int Encoder::getCpr(){return CPR;}