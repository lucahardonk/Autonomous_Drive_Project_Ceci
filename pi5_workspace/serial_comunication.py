#!/usr/bin/env python3
import serial
import json
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
PORT = "/dev/serial/by-id/usb-Arduino_UNO_R4_Minima_3806171436313637915533334B572F2B-if00"
BAUD = 1_000_000
SEND_PERIOD = 0.01  # 10 ms → 100 Hz

app = Flask(__name__)
CORS(app)
# Shared state
latest_feedback = {}
command_lock = threading.Lock()
current_command = {
    "cmd": {
        "motorLeftPwm": 0,
        "motorRightPwm": 0,
        "direction": 1,
        "steerAngle": 0
    }
}

# ─────────────────────────────────────────────
# Serial setup
# ─────────────────────────────────────────────
def open_serial():
    ser = serial.Serial(PORT, BAUD, timeout=0.01)
    print(f"✅ Connected to {PORT} @ {BAUD} baud")
    return ser

# ─────────────────────────────────────────────
# Background serial reader
# ─────────────────────────────────────────────
def read_serial(ser):
    global latest_feedback
    buffer = ""
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode(errors="ignore")
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        doc = json.loads(line)
                        if "fb" in doc:
                            latest_feedback = doc["fb"]
                    except json.JSONDecodeError:
                        pass  # skip bad JSON
        except serial.SerialException:
            print("❌ Serial disconnected.")
            break
        except Exception as e:
            print(f"⚠️ Read error: {e}")

# ─────────────────────────────────────────────
# Background serial writer
# ─────────────────────────────────────────────
def write_serial(ser):
    while True:
        with command_lock:
            msg = json.dumps(current_command)
        ser.write((msg + "\n").encode())
        time.sleep(SEND_PERIOD)

# ─────────────────────────────────────────────
# Flask endpoints
# ─────────────────────────────────────────────

@app.route("/cmd", methods=["POST"])
def set_command():
    """Send JSON command to Arduino."""
    try:
        data = request.get_json(force=True)
        if not data or "cmd" not in data:
            return jsonify({"error": "Missing 'cmd' object"}), 400

        with command_lock:
            current_command["cmd"].update(data["cmd"])
        return jsonify({"status": "ok", "current_cmd": current_command})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/feedback", methods=["GET"])
def get_feedback():
    """Return latest feedback JSON from Arduino."""
    return jsonify({"fb": latest_feedback})


@app.route("/")
def index():
    return jsonify({
        "info": "Arduino Car Serial Web API",
        "endpoints": {
            "POST /cmd": "Send new command JSON to Arduino",
            "GET /feedback": "Get latest feedback",
        }
    })

# ─────────────────────────────────────────────
# Main entrypoint
# ─────────────────────────────────────────────
def main():
    ser = open_serial()

    reader = threading.Thread(target=read_serial, args=(ser,), daemon=True)
    writer = threading.Thread(target=write_serial, args=(ser,), daemon=True)
    reader.start()
    writer.start()

    app.run(host="0.0.0.0", port=5000, threaded=True)

# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()


# curl -X POST http://192.168.1.149:5000/cmd -H "Content-Type: application/json" -d '{"cmd":{"motorLeftPwm":120,"motorRightPwm":120,"direction":1,"steerAngle":15}}'
# curl http://192.168.1.149:5000/feedback