#include <ArduinoJson.h>
#include <Car.h>

Car myCar;
unsigned long lastFeedback = 0;

// Command variables
int motorLeftPwm = 0;
int motorRightPwm = 0;
int direction = 1; 
int steerAngle = 0;


void setup() {
  Serial.begin(1000000);
  myCar.begin();
  myCar.resetEncoders();
  Serial.println(F("🚗 Car ready for JSON serial control"));


}

// ─────────────────────────────────────────────
// Main loop
// ─────────────────────────────────────────────
void loop() {

  handleSerialJson(); // process incoming JSON
  myCar.steer(steerAngle);
  myCar.drive(motorLeftPwm, motorRightPwm, direction);

  if (millis() - lastFeedback > 1000) {   // send every 10 ms
    sendFeedback();
    lastFeedback = millis();
  }
}

// ─────────────────────────────────────────────
// Parse JSON command from serial
// ─────────────────────────────────────────────
void handleSerialJson() {
  static String input;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      StaticJsonDocument<256> doc;
      DeserializationError err = deserializeJson(doc, input);
      if (!err && doc.containsKey("cmd")) {
        JsonObject cmd = doc["cmd"];
        motorLeftPwm  = constrain(cmd["motorLeftPwm"]  | 0, 0, 255);
        motorRightPwm = constrain(cmd["motorRightPwm"] | 0, 0, 255);
        direction     = constrain(cmd["direction"]     | 1, -1, 1);
        steerAngle    = constrain(cmd["steerAngle"]    | 0, -90, 90);
      }
      input = "";
    } else {
      input += c;
    }
  }
}

// ─────────────────────────────────────────────
// Send JSON feedback to Raspberry Pi
// ─────────────────────────────────────────────
void sendFeedback() {
  long leftCount  = myCar.getLeftEncoderCount();
  long rightCount = myCar.getRightEncoderCount();

  float wheelLeftW  = myCar.getLeftEncoderVelocity();
  float wheelRightW = myCar.getRightEncoderVelocity();

  StaticJsonDocument<256> doc;
  JsonObject fb = doc.createNestedObject("fb");
  fb["wheelLeftCount"]  = leftCount;
  fb["wheelLeftW"]      = wheelLeftW;
  fb["wheelRightCount"] = rightCount;
  fb["wheelRightW"]     = wheelRightW;

  serializeJson(doc, Serial);
  Serial.println();
}  
