#ifndef WEBCONTROL_H
#define WEBCONTROL_H

#include <WiFiS3.h>
#include <ArduinoHttpServer.h>

class WebControlClass {
public:
  void begin();
  void handleClient();

private:
  void handleRequest(WiFiClient& client);
  void handleCommand(const String& path, ArduinoHttpServer::StreamHttpReply& reply);
  void handleRoot(ArduinoHttpServer::StreamHttpReply& reply);
};

// Global instance
extern WebControlClass WebControl;

#endif
