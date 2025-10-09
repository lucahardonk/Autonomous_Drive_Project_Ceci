#include <Servo.h>  
#include <WiFiS3.h>

#include "WebControl.h"
#include "Motor.h"   
#include "Encoder.h" 
#include "Sterzo.h"

const char* ssid = "casa_wireless";
const char* password = "wireless_casa_88";

// ── Servo ──────────────────────
Sterzo sterzo;

// ── Encoder ──────────────────────
Encoder leftEncoder(2, 3, 836);
Encoder rightEncoder(12, 8, 836);


// ── Motors ──────────────────────

Motor leftMotor  (5, 6);
Motor rightMotor (9, 10);

void setup() {
  Serial.begin(115200);
  leftMotor.begin();
  rightMotor.begin();
  sterzo.attach(11);
  sterzo.set(0); 
  Serial.println("starting...");


  
  rightEncoder.begin();
  leftEncoder.begin();


  // wireless initialization

  Serial.println("\nConnecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ Connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  WebControl.begin();   // Start web server
 
}


// ── Serial Command Buffer ───────────────────────────────
String cmdBuffer = "";

void loop() {
  
// ── Read incoming serial characters ──────────────────
  while (Serial.available()) {
    char c = Serial.read();
    if (c == ';') {
      processCommand(cmdBuffer);
      cmdBuffer = "";
    } else {
      cmdBuffer += c;
    }
  }

/*
  leftEncoder.printState();
  Serial.print(",");
  rightEncoder.printState();
  Serial.println(" ");*/

  WebControl.handleClient(); // Keep serving requests
}

// ── Command Parser ───────────────────────────────
void processCommand(String cmd) {
  cmd.trim();  // remove spaces/newlines

  //Serial.print("→ Received: ");
  //Serial.println(cmd);

  // ── Motor Commands ───────────────────────
  if (cmd.startsWith("leftMotor.Forward(")) {
    int val = extractValue(cmd);
    leftMotor.Forward(val);
  }
  else if (cmd.startsWith("rightMotor.Forward(")) {
    int val = extractValue(cmd);
    rightMotor.Forward(val);
  }
  else if (cmd.startsWith("leftMotor.Backward(")) {
    int val = extractValue(cmd);
    leftMotor.Backward(val);
  }
  else if (cmd.startsWith("rightMotor.Backward(")) {
    int val = extractValue(cmd);
    rightMotor.Backward(val);
  }
  else if (cmd.startsWith("leftMotor.Stop()")) {
    leftMotor.Stop();
  }
  else if (cmd.startsWith("rightMotor.Stop()")) {
    rightMotor.Stop();
  }
  else if (cmd.startsWith("sterzo.set(")) {
    int val = extractValue(cmd);
    sterzo.set(val);
  }
  else {
    Serial.println("⚠️ Unknown command");
  }


  
}

// ── Utility: Extract int value from parentheses ───────────────
int extractValue(String cmd) {
  int start = cmd.indexOf('(');
  int end   = cmd.indexOf(')');
  if (start == -1 || end == -1) return 0;
  String num = cmd.substring(start + 1, end);
  num.trim();
  return num.toInt();
}

/*
setSterzo(+5);
setSterzo(-10);
setSterzo(0);

leftMotor.Forward(100);
leftMotor.Backward(150);
leftMotor.Stop();

rightMotor.Forward(100);
rightMotor.Backward(150);
rightMotor.Stop();

*/

