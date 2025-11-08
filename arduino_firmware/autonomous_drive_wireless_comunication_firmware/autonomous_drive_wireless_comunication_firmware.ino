#include "Secret.h"
#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <Car.h>
Car myCar;

// Encoder counts per revolution of the WHEEL

// Command variables
int motorLeftPwm = 0;
int motorRightPwm = 0;
int direction = 1;
int steerAngle = 0;

// json
StaticJsonDocument<256> jsonOut;
StaticJsonDocument<256> jsonIn;


// ── Wi-Fi settings ───────────────────────────────
const char* ssid     = MySSID;
const char* password = MyPWD;

// ── UDP settings ────────────────────────────────
WiFiUDP udpOut;
WiFiUDP udpIn;
const unsigned int udpOutPort = 9084;
const unsigned int udpInPort  = 9085;
const char* broadcastIp = "192.168.1.255";

// ── Variabili calcolo RPM ───────────────────────
static long prevL = 0, prevR = 0;
static unsigned long prevTime = 0;

// ── Setup ───────────────────────────────────────
void setup() {
  Serial.begin(115200);
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

// ── Loop ───────────────────────────────────────
void loop() {
  unsigned long now = millis();

  if (now - prevTime >= 20) {  // 50 Hz
    long Lc = myCar.getLeftEncoderCount();
    long Rc = myCar.getRightEncoderCount();

    //long dL = Lc - prevL;
    //long dR = Rc - prevR;
    //float dt = (now - prevTime) / 1000.0f;
    //if (dt <= 0) dt = 1e-3f;

   // Rad/s motore (calcolati dall’encoder)
    float LW = myCar.leftEncoder.getVelocity();
    float RW = myCar.rightEncoder.getVelocity();

    // Rad/s → RPM calcolati fisici
    float L_RPM = LW * (60.0f / (2.0f * PI));
    float R_RPM = RW * (60.0f / (2.0f * PI));

    // Applico la correzione sperimentale: Tachometer ≈ 2.783 * calcolati
    L_RPM = 2.783f * L_RPM;
    R_RPM = 2.783f * R_RPM;

    jsonOut.clear();
    jsonOut["time"] = now;
    jsonOut["LCount"] = Lc;
    jsonOut["L_RPM"] = L_RPM;
    jsonOut["RCount"] = Rc;
    jsonOut["R_RPM"] = R_RPM;

    sendJson(jsonOut, broadcastIp, udpOutPort);


    prevL = Lc;
    prevR = Rc;
    prevTime = now;
  }

  if (receiveJson(jsonIn)) {
    motorLeftPwm  = constrain(jsonIn["LPwm"] | 0, 0, 255);
    motorRightPwm = constrain(jsonIn["RPwm"] | 0, 0, 255);
    direction     = constrain(jsonIn["D"]    | 1, -1, 1);
    steerAngle    = constrain(jsonIn["S"]   | 0, -90, 90);

    myCar.steer(steerAngle);
    myCar.drive(motorLeftPwm, motorRightPwm, direction);
  }
}

// ── Send JSON helper ────────────────────────────
void sendJson(const JsonDocument& doc, const char* ip, int port) {
  String json;
  serializeJson(doc, json);
  json += "\n";
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

    DeserializationError err = deserializeJson(doc, buffer);
    if (err) return false;
    return true;
  }
  return false;
}

String jsonToString(const JsonDocument& doc) {
  String s;
  serializeJson(doc, s);
  return s;
}
