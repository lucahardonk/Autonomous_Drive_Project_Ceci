#include "WebControl.h"
#include "Sterzo.h"
#include <WiFiUdp.h>
using namespace ArduinoHttpServer;

WiFiUDP udp;
WebControlClass WebControl;
extern void processCommand(String cmd);
extern Sterzo sterzo;  // definito nel main.ino

void WebControlClass::begin() {
  udp.begin(8888);
  Serial.println("📡 UDP control server started on port 8888");
}

void WebControlClass::handleClient() {
  int packetSize = udp.parsePacket();
  if (packetSize <= 0) return;

  char buffer[128];
  int len = udp.read(buffer, sizeof(buffer) - 1);
  if (len <= 0) return;
  buffer[len] = '\0';

  handleRequest(buffer);
}

void WebControlClass::handleRequest(const char* body) {
  float x = 0.0, y = 0.0, z = 0.0;

  // Quick JSON parse (simple & fast)
  String msg(body);
  int xi = msg.indexOf("\"x\":");
  int yi = msg.indexOf("\"y\":");
  int zi = msg.indexOf("\"z\":");

  if (xi >= 0) x = msg.substring(xi + 4, msg.indexOf(",", xi)).toFloat();
  if (yi >= 0) y = msg.substring(yi + 4, msg.indexOf(",", yi)).toFloat();
  if (zi >= 0) z = msg.substring(zi + 4).toFloat();

  auto clamp = [](float v, float minV, float maxV) {
    return (v < minV) ? minV : (v > maxV ? maxV : v);
  };
  x = clamp(x, -1.0, 1.0);
  y = clamp(y, -1.0, 1.0);
  z = clamp(z, -1.0, 1.0);

  // === Controllo motori ===
  int speed = abs(x) * 255;
  if (x > 0.05) {
    processCommand("leftMotor.Forward(" + String(speed) + ")");
    processCommand("rightMotor.Forward(" + String(speed) + ")");
  } else if (x < -0.05) {
    processCommand("leftMotor.Backward(" + String(speed) + ")");
    processCommand("rightMotor.Backward(" + String(speed) + ")");
  } else {
    processCommand("leftMotor.Stop()");
    processCommand("rightMotor.Stop()");
  }

  // === Sterzo ===
  int steerAngle = int(y * 70);
  processCommand("sterzo.set(" + String(steerAngle) + ")");

  // === Pulsante Z ===
  if (z > 0.5) {
    processCommand("leftMotor.Stop()");
    processCommand("rightMotor.Stop()");
  }

  // Debug frequency print (optional)
  static unsigned long last = 0;
  unsigned long now = millis();
  if (last > 0) {
    float dt = now - last;
    float hz = 1000.0 / dt;
    Serial.print("[UDP] ");
    Serial.print(hz, 1);
    Serial.println(" Hz");
  }
  last = now;
}
