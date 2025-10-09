#include "Encoder.h"

// Static members
Encoder* Encoder::encoder0 = nullptr;
Encoder* Encoder::encoder1 = nullptr;

void Encoder::begin() {
  pinMode(pinA, INPUT_PULLUP);
  pinMode(pinB, INPUT_PULLUP);
  lastState = (digitalRead(pinA) << 1) | digitalRead(pinB);

  // Assign to first available slot
  if (!encoder0) encoder0 = this;
  else if (!encoder1) encoder1 = this;

  // Attach ISRs depending on slot
  if (encoder0 == this) {
    attachInterrupt(digitalPinToInterrupt(pinA), handleInterruptA, CHANGE);
    attachInterrupt(digitalPinToInterrupt(pinB), handleInterruptA, CHANGE);
  } else if (encoder1 == this) {
    attachInterrupt(digitalPinToInterrupt(pinA), handleInterruptB, CHANGE);
    attachInterrupt(digitalPinToInterrupt(pinB), handleInterruptB, CHANGE);
  }
}

void Encoder::handleInterruptA() {
  if (encoder0) encoder0->update();
}
void Encoder::handleInterruptB() {
  if (encoder1) encoder1->update();
}

void Encoder::update() {
  uint8_t currentState = (digitalRead(pinA) << 1) | digitalRead(pinB);
  uint8_t transition = (lastState << 2) | currentState;

  // Quadrature lookup table
  static const int8_t table[16] = {
      0, +1, -1, 0,
     -1,  0,  0, +1,
     +1,  0,  0, -1,
      0, -1, +1, 0
  };

  position += table[transition];
  lastState = currentState;
}

void Encoder::printState() {
  noInterrupts();
  long pos = position;
  interrupts();
  Serial.print(pos);
}
