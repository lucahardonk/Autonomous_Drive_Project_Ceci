#include "Secret.h"
#include <WiFiS3.h>
#include <WiFiUDP.h>
#include <ArduinoJson.h>
#include <Car.h>
Car myCar;


// Command variables
int motorLeftPwm = 0;
int motorRightPwm = 0;
int direction = 1;
int steerAngle = 0;



// ── Wi-Fi settings ───────────────────────────────
const char* ssid     = MySSID;
const char* password = MyPWD;

// ── UDP settings ────────────────────────────────
WiFiUDP udpOut;
WiFiUDP udpIn;
const unsigned int udpOutPort = 9084;
const unsigned int udpInPort  = 9085;
const char* broadcastIp = "192.168.1.255";

// ── Variables ───────────────────────────────────
unsigned long lastSend = 0;

// ── Global JSON documents ───────────────────────
StaticJsonDocument<256> jsonIn;   // for received data
StaticJsonDocument<256> jsonOut;  // for outgoing data

// ── Function prototypes ─────────────────────────
void sendJson(const JsonDocument& doc, const char* ip, int port);
bool receiveJson(JsonDocument& doc);
String jsonToString(const JsonDocument& doc);

// ── Setup ───────────────────────────────────────
void setup() {
  Serial.begin(115200);

  //car begin 
  myCar.begin();
  myCar.resetEncoders();


  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("✅ Connected! IP: ");
  Serial.println(WiFi.localIP());

  udpOut.begin(udpOutPort);
  udpIn.begin(udpInPort);
  Serial.println("📡 Ready: broadcasting on 9084, listening on 9085");
}

// ── Loop ────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  // ── Populate jsonOut and broadcast every 20 ms ─
  if (now - lastSend >= 20) {
    lastSend = now;

    jsonOut.clear();
    jsonOut["time"] = now;
    jsonOut["leftCount"] = myCar.getLeftEncoderCount();
    jsonOut["wheelLeftW"] = myCar.getLeftEncoderVelocity();
    jsonOut["rightCount"] = myCar.getRightEncoderCount();
    jsonOut["wheelRightW"] = myCar.getRightEncoderVelocity();

    sendJson(jsonOut, broadcastIp, udpOutPort);
  }

  // ── Receive JSON messages into jsonIn ──────────
  if (receiveJson(jsonIn)) {
    motorLeftPwm  = constrain(jsonIn["motorLeftPwm"]  | 0,   0,   255);
    motorRightPwm = constrain(jsonIn["motorRightPwm"] | 0,   0,   255);
    direction     = constrain(jsonIn["direction"]     | 1,  -1,    1);
    steerAngle    = constrain(jsonIn["steerAngle"]    | 0,  -90,   90);

      // ✅ Apply commands to the car
    myCar.drive(motorLeftPwm, motorRightPwm, direction);
    myCar.steer(steerAngle);

    /*
      Serial.println("➡️ Command received:");
      Serial.print("  Left PWM: ");   Serial.println(motorLeftPwm);
      Serial.print("  Right PWM: ");  Serial.println(motorRightPwm);
      Serial.print("  Direction: ");  Serial.println(direction);
      Serial.print("  Steer angle: ");Serial.println(steerAngle);
    */


  }
  
}


// ── Send JSON helper ────────────────────────────
void sendJson(const JsonDocument& doc, const char* ip, int port) {
  String json;
  serializeJson(doc, json);
  json += "\n";  // 👈 add newline
  udpOut.beginPacket(ip, port);
  udpOut.write(json.c_str());
  udpOut.endPacket();
}


// ── Receive JSON helper ─────────────────────────
bool receiveJson(JsonDocument& doc) {
  int packetSize = udpIn.parsePacket();
  if (packetSize > 0) {
    char buffer[256];
    int len = udpIn.read(buffer, sizeof(buffer) - 1);
    if (len > 0) buffer[len] = '\0';
    /*
    Serial.print("📥 Received: ");
    Serial.println(buffer);
    */
    DeserializationError err = deserializeJson(doc, buffer);
    if (err) {
      Serial.print("⚠️ JSON parse error: ");
      Serial.println(err.c_str());
      return false;
    }
    return true;
  }
  return false;
}

// ── Utility: Convert JSON to string ─────────────
String jsonToString(const JsonDocument& doc) {
  String s;
  serializeJson(doc, s);
  return s;
}
