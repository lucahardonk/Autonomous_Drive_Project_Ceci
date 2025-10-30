import socket, json, pygame, time

# === Network configuration ===
UDP_IP = "192.168.1.162"     # Arduino R4 WiFi IP
UDP_PORT = 9085              # UDP port number

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === Initialize joystick ===
pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

print(f"🎮 Sending joystick data to {UDP_IP}:{UDP_PORT} at 50 Hz")

# === State variables ===
direction = 0
forward_prev = 0
backward_prev = 0

# === Helper functions ===
def map_range(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return out_min + (float(value - in_min) * (out_max - out_min) / (in_max - in_min))

# === Main loop ===
while True:
    pygame.event.pump()

    # --- Read joystick inputs ---
    steer = j.get_axis(0)       # -1 = left, +1 = right
    gas = j.get_axis(5)         # -1 = not pressed, +1 = fully pressed
    brake = j.get_axis(2)       # -1 = not pressed, +1 = fully pressed
    forward = j.get_button(5)   # Button 5: toggle forward/neutral
    backward = j.get_button(4)  # Button 4: toggle backward/neutral

    # --- Toggle direction (edge detection) ---
    if forward and not forward_prev:
        if direction == -1:
            direction = 0
        elif direction == 0:
            direction = 1
    if backward and not backward_prev:
        if direction == 1:
            direction = 0
        elif direction == 0:
            direction = -1

    forward_prev = forward
    backward_prev = backward

    # --- Normalize pedals ---
    gas_norm = (gas + 1) / 2      # 0–1
    brake_norm = (brake + 1) / 2  # 0–1

    # --- Base PWM based on gas ---
    base_pwm = int(gas_norm * 255)

    # --- Apply brake ---
    if brake_norm > 0.7:
        base_pwm = 0

    # --- Steering mapping (-1..1 → -90..90 degrees) ---
    steerAngle = int(map_range(steer, -1, 1, -90, 90))

    # --- Differential steering ---
    # Slightly reduce one wheel when steering
    motorLeftPwm  = base_pwm
    motorRightPwm = base_pwm
    if steer < -0.05:   # turning left
        motorLeftPwm  = int(base_pwm)
    elif steer > 0.05:  # turning right
        motorRightPwm = int(base_pwm)

    # --- Build JSON command ---
    msg = json.dumps({
        "LPwm":  motorLeftPwm,
        "RPwm": motorRightPwm,
        "D":     direction,
        "S":    steerAngle
    })

    # --- Send UDP ---
    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

    # --- Debug ---
    dir_str = { -1: "BACKWARD", 0: "NEUTRO", 1: "FORWARD" }[direction]
    print(f"Dir: {dir_str:8s} | Gas={gas_norm:.2f} | Brake={brake_norm:.2f} | "
          f"Steer={steerAngle:4d} | L={motorLeftPwm:3d} | R={motorRightPwm:3d}")

    time.sleep(0.02)  # 50 Hz

