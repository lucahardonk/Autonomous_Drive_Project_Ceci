#include <Car.h>

Car myCar;
unsigned long lastPrint = 0;

void setup() {
  Serial.begin(115200);
  myCar.begin();
  Serial.println("🚗 Car ready!");
  delay(1000);
  myCar.resetEncoders();
}

void loop() {

  
  
   // ─────────────────────────────────────────────
  //  FORWARD TEST
  // ─────────────────────────────────────────────
  Serial.println("\n➡️  Driving forward with steering test...");

  myCar.steer(-20);   // turn slightly left
  myCar.drive(200, 200, 1);
  printEncoderFeedback(2000);

  myCar.steer(0);     // center
  myCar.drive(200, 200, 1);
  printEncoderFeedback(2000);

  myCar.steer(20);    // turn slightly right
  myCar.drive(200, 200, 1);
  printEncoderFeedback(2000);

  myCar.stop();
  delay(1000);

  // ─────────────────────────────────────────────
  //  BACKWARD TEST
  // ─────────────────────────────────────────────
  Serial.println("\n⬅️  Driving backward with steering test...");

  myCar.steer(20);    // turn slightly right
  myCar.drive(200, 200, -1);
  printEncoderFeedback(2000);

  myCar.steer(0);     // center
  myCar.drive(200, 200, -1);
  printEncoderFeedback(2000);

  myCar.steer(-20);   // turn slightly left
  myCar.drive(200, 200, -1);
  printEncoderFeedback(2000);

  myCar.stop();
  delay(1500);
  
  

  printEncoderFeedback(2000);

  myCar.stop();
 
}

// ─────────────────────────────────────────────
// Helper function: prints encoder feedback
// ─────────────────────────────────────────────
void printEncoderFeedback(unsigned long durationMs) {
  unsigned long start = millis();
  while (millis() - start < durationMs) {
    // continuously update encoders
    long leftCount = myCar.getLeftEncoderCount();
    long rightCount = myCar.getRightEncoderCount();

    if (millis() - lastPrint > 200) {
      Serial.print("  Left encoder: ");
      Serial.print(leftCount);
      Serial.print(" | Right encoder: ");
      Serial.println(rightCount);
      lastPrint = millis();
    }
  }
}
