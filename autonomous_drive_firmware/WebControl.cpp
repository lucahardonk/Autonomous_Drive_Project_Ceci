#include "WebControl.h"
#include "Sterzo.h"
using namespace ArduinoHttpServer;

WiFiServer wifiServer(80);
WebControlClass WebControl;
extern void processCommand(String cmd);
extern Sterzo sterzo;  // from your main.ino

void WebControlClass::begin() {
  wifiServer.begin();
  Serial.println("🌐 Web API server started on port 80");
}

void WebControlClass::handleClient() {
  WiFiClient client = wifiServer.available();
  if (!client) return;
  handleRequest(client);
  client.stop();
}

void WebControlClass::handleRequest(WiFiClient& client) {
  StreamHttpRequest<512> request(client);
  if (!request.readRequest()) return;

  String path = request.getResource().toString();
  StreamHttpReply reply(client, "application/json");

  // Enable CORS for browser access
  reply.addHeader("Access-Control-Allow-Origin", "*");
  reply.addHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  reply.addHeader("Access-Control-Allow-Headers", "Content-Type");

  static int currentSpeed = 0;
  static int currentSteer = 0;

  auto clamp = [](int val, int minV, int maxV) {
    return (val < minV) ? minV : (val > maxV ? maxV : val);
  };

  // === API ROUTES ===
  if (path == "/forward") {
    currentSpeed = clamp(currentSpeed + 10, 0, 255);
    handleCommand("leftMotor.Forward(" + String(currentSpeed) + ")", reply);
    handleCommand("rightMotor.Forward(" + String(currentSpeed) + ")", reply);
    reply.send("{\"action\":\"forward\",\"speed\":" + String(currentSpeed) + "}");
    Serial.println("🚗 Forward");
  }

  else if (path == "/backward") {
    currentSpeed = clamp(currentSpeed + 10, 0, 255);
    handleCommand("leftMotor.Backward(" + String(currentSpeed) + ")", reply);
    handleCommand("rightMotor.Backward(" + String(currentSpeed) + ")", reply);
    reply.send("{\"action\":\"backward\",\"speed\":" + String(currentSpeed) + "}");
    Serial.println("🔙 Backward");
  }

  else if (path.startsWith("/steer")) {
    int val = 0;
    int idx = path.indexOf("val=");
    if (idx >= 0) val = path.substring(idx + 4).toInt();
    currentSteer = clamp(val, -70, 70);
    handleCommand("sterzo.set(" + String(currentSteer) + ")", reply);
    reply.send("{\"action\":\"steer\",\"angle\":" + String(currentSteer) + "}");
  }

  else if (path == "/stop") {
    currentSpeed = 0;
    currentSteer = 0;
    handleCommand("leftMotor.Stop()", reply);
    handleCommand("rightMotor.Stop()", reply);
    handleCommand("sterzo.set(0)", reply);
    reply.send("{\"action\":\"stop\",\"speed\":0,\"steer\":0}");
    Serial.println("🛑 Stop");
  }

  else if (path == "/steer/limits") {
    String json = "{";
    json += "\"minLeft\":" + String(sterzo.getMinLeft()) + ",";
    json += "\"maxRight\":" + String(sterzo.getMaxRight()) + ",";
    json += "\"center\":" + String(sterzo.getCenter());
    json += "}";
    reply.send(json);
  }

  else {
    reply.send("{\"status\":\"ok\",\"info\":\"UNO R4 WiFi API ready\"}");
  }
}

void WebControlClass::handleCommand(const String& cmd, StreamHttpReply& reply) {
  processCommand(cmd);
}