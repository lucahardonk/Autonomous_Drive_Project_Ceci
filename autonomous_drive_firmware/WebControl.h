#ifndef WEBCONTROL_H
#define WEBCONTROL_H

#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <ArduinoHttpServer.h>

class WebControlClass {
public:
  void begin();
  void handleClient();

private:
  void handleRequest(const char* body);
};

// Global instance
extern WebControlClass WebControl;

#endif
