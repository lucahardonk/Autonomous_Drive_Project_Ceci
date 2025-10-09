#include "WebControl.h"
using namespace ArduinoHttpServer;

WiFiServer wifiServer(80);
WebControlClass WebControl;

extern void processCommand(String cmd);

// ─────────────── BEGIN ───────────────
void WebControlClass::begin() {
  wifiServer.begin();
  Serial.println("🌐 Web server started on port 80");
}

// ─────────────── LOOP HANDLER ───────────────
void WebControlClass::handleClient() {
  WiFiClient client = wifiServer.available();
  if (!client) return;

  handleRequest(client);
  client.stop();
}

// ─────────────── REQUEST HANDLER ───────────────
void WebControlClass::handleRequest(WiFiClient& client) {
  // Create parser for HTTP request
  StreamHttpRequest<512> request(client);
  if (!request.readRequest()) return;

  String path = request.getResource().toString();
  StreamHttpReply reply(client, "text/html");

  // ── Persistent variables ───────────────────────────────
  static int currentSpeed = 0;   // ±255 or whatever your PWM max
  static int currentSteer = 0;   // ±90 or whatever range you use

  // Clamp helpers
  auto clamp = [](int val, int minV, int maxV) {
    return (val < minV) ? minV : (val > maxV ? maxV : val);
  };

  // ── Route handling ───────────────────────────────
  if (path == "/forward") {
    currentSpeed = clamp(currentSpeed + 10, 0, 255);  // increase speed
    handleCommand("leftMotor.Forward(" + String(currentSpeed) + ")", reply);
    handleCommand("rightMotor.Forward(" + String(currentSpeed) + ")", reply);
    Serial.print("🚗 Speed ↑ ");
    Serial.println(currentSpeed);
  }
  else if (path == "/backward") {
    currentSpeed = clamp(currentSpeed - 10, -255, 255);  // negative values mean backward
    if (currentSpeed >= 0) {
      handleCommand("leftMotor.Forward(" + String(currentSpeed) + ")", reply);
      handleCommand("rightMotor.Forward(" + String(currentSpeed) + ")", reply);
    } else {
      handleCommand("leftMotor.Backward(" + String(abs(currentSpeed)) + ")", reply);
      handleCommand("rightMotor.Backward(" + String(abs(currentSpeed)) + ")", reply);
    }
    Serial.print("🚗 Speed ↓ ");
    Serial.println(currentSpeed);
  }
  else if (path == "/left") {
    currentSteer = clamp(currentSteer - 10, -70, 70);   // limit steering angle
    handleCommand("setSterzo(" + String(currentSteer) + ")", reply);
    Serial.print("↩️ Steer Left: ");
    Serial.println(currentSteer);
  }
  else if (path == "/right") {
    currentSteer = clamp(currentSteer + 10, -70, 70);
    handleCommand("setSterzo(" + String(currentSteer) + ")", reply);
    Serial.print("↪️ Steer Right: ");
    Serial.println(currentSteer);
  }
  else if (path == "/stop") {
    currentSpeed = 0;
    currentSteer = 0;
    handleCommand("leftMotor.Stop()", reply);
    handleCommand("rightMotor.Stop()", reply);
    handleCommand("setSterzo(0)", reply);
    Serial.println("🛑 Stop pressed — reset speed & steering");
  }
  else {
    handleRoot(reply);
  }
}

// ─────────────── COMMAND HANDLER ───────────────
void WebControlClass::handleCommand(const String& cmd, StreamHttpReply& reply) {
  processCommand(cmd);
  reply.send("OK");
}


// ─────────────── HTML ROOT PAGE ───────────────
void WebControlClass::handleRoot(StreamHttpReply& reply) {
  String html = R"rawliteral(
  <!DOCTYPE html>
  <html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>UNO R4 WiFi Car Controller</title>
    <style>
      body {
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        height:100vh;background:#111;color:#fff;font-family:sans-serif;
      }
      .grid {
        display:grid;
        grid-template-areas:
          ". up ."
          "left stop right"
          ". down .";
        gap:20px;
      }
      button {
        width:80px;height:80px;border:none;border-radius:15px;
        background:#333;color:#fff;font-size:32px;
        cursor:pointer;transition:0.2s;
      }
      button:hover{background:#555;transform:scale(1.1);}
      button:active{background:#777;}
      #up{grid-area:up;}
      #down{grid-area:down;}
      #left{grid-area:left;}
      #right{grid-area:right;}
      #stop{grid-area:stop;background:#a00;}
    </style>
  </head>
  <body>
    <h2>UNO R4 WiFi Car Controller</h2>
    <div class="grid">
      <button id="up"    onclick="send('forward')">↑</button>
      <button id="left"  onclick="send('left')">←</button>
      <button id="stop"  onclick="send('stop')">⏹</button>
      <button id="right" onclick="send('right')">→</button>
      <button id="down"  onclick="send('backward')">↓</button>
    </div>
    <script>
      function send(cmd){
        fetch('/'+cmd)
          .then(()=>console.log('Sent:',cmd))
          .catch(e=>alert('Error:'+e));
      }
    </script>
  </body>
  </html>
  )rawliteral";

  reply.send(html);
}
