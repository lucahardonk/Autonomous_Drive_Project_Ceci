import pygame
import requests
import time

# === CONFIGURATION ===
API_BASE = "http://192.168.1.162"   # ← change to your ESP or server IP
DEADZONE = 0.05

# === INIT JOYSTICK ===
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"🎮 Controller: {joystick.get_name()}")
print(f"Axes: {joystick.get_numaxes()}, Buttons: {joystick.get_numbuttons()}")

current_speed = 0
last_steer = 0
direction = "forward"  # 💡 track current direction

def clamp(val, minv, maxv):
    return max(min(val, maxv), minv)

while True:
    pygame.event.pump()

    # === AXES ===
    steer = joystick.get_axis(0)
    gas = joystick.get_axis(5)
    brake = joystick.get_axis(2)

    gas = (gas + 1) / 2
    brake = (brake + 1) / 2

    # === BUTTONS ===
    forward_btn = joystick.get_button(5)
    backward_btn = joystick.get_button(4)

    # === UPDATE DIRECTION ===
    if forward_btn:
        direction = "forward"
        print("→ Direction set to FORWARD")
        time.sleep(0.2)

    if backward_btn:
        direction = "backward"
        print("← Direction set to BACKWARD")
        time.sleep(0.2)

    # === STEERING ===
    if abs(steer - last_steer) > DEADZONE:
        angle = int(clamp(steer * 70, -70, 70))
        try:
            requests.get(f"{API_BASE}/steer?val={angle}", timeout=0.1)
            print(f"Steering → {angle}")
        except requests.RequestException:
            pass
        last_steer = steer

    # === GAS CONTROL ===
    if gas > 0.1:
        speed = int(gas * 255)
        try:
            requests.get(f"{API_BASE}/{direction}", timeout=0.1)
            print(f"🚗 {direction.capitalize()} speed: {speed}")
        except requests.RequestException:
            pass

    # === BRAKE ===
    if brake > 0.5:
        try:
            requests.get(f"{API_BASE}/stop", timeout=0.1)
            print("🛑 Brake")
        except requests.RequestException:
            pass

    time.sleep(0.05)
