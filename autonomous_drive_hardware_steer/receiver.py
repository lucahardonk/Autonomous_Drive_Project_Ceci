import asyncio
import websockets
import json
import socket
import threading

# UDP setup
UDP_IP = "0.0.0.0"
UDP_PORT = 9084

latest_telemetry = {"LCount": 0, "LW": 0, "RCount": 0, "RW": 0}

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"📥 Listening UDP on port {UDP_PORT}...")

    while True:
        data, _ = sock.recvfrom(1024)
        try:
            telemetry = json.loads(data.decode())
            latest_telemetry.update(telemetry)

            print(f"LCount: {latest_telemetry['LCount']}, "
                  f"LW:   {latest_telemetry['LW']:.2f}, "
                  f"RCount: {latest_telemetry['RCount']}, "
                  f"RW:   {latest_telemetry['RW']:.2f}")

        except Exception as e:
            print("⚠️ JSON Error:", e)


async def ws_handler(websocket):
    print("✅ Web client connected")
    while True:
        data_to_send = json.dumps(latest_telemetry)

        # ✅ Debug print for Web UI transmission
        print("📤 Sending to Web UI:", data_to_send)

        await websocket.send(data_to_send)
        await asyncio.sleep(0.02)




def start_udp_thread():
    udp_thread = threading.Thread(target=udp_listener, daemon=True)
    udp_thread.start()


start_udp_thread()

async def main():
    # ✅ Binding on all interfaces
    async with websockets.serve(ws_handler, "0.0.0.0", 8080, ping_interval=None):
        print("🌍 WebSocket server running on ws://0.0.0.0:8080")
        await asyncio.Future()  # keep running forever

asyncio.run(main())
