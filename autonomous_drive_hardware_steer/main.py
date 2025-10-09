import socket, json, pygame, time

# === Network configuration ===
UDP_IP = "192.168.1.162"   # Arduino R4 WiFi IP
UDP_PORT = 8888            # UDP port on Arduino

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === Initialize joystick ===
pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

print(f"🎮 Sending joystick data to {UDP_IP}:{UDP_PORT} at 50 Hz")

# === State ===
direction = "STOP"

while True:
    pygame.event.pump()

    # --- Read joystick values ---
    steer = j.get_axis(0)       # axes[0]: steering (-1 left → +1 right)
    gas = j.get_axis(5)         # axes[5]: gas pedal (-1 default → +1 max)
    brake = j.get_axis(2)       # axes[2]: brake pedal (-1 default → +1 max)
    forward = j.get_button(5)   # button[5]: set direction to FORWARD
    backward = j.get_button(4)  # button[4]: set direction to BACKWARD

    # --- Normalize pedals ---
    gas_norm = (gas + 1) / 2    # -1 → 0, +1 → 1
    brake_norm = (brake + 1) / 2

    # --- Latch direction ---
    if forward:
        direction = "FORWARD"
    elif backward:
        direction = "BACKWARD"

    # --- Determine movement based on gas pedal and direction ---
    if gas_norm > 0.05:  # threshold to ignore noise
        if direction == "FORWARD":
            x = gas_norm
        elif direction == "BACKWARD":
            x = -gas_norm
        else:
            x = 0.0
    else:
        x = 0.0  # no gas → no movement

    # --- Optional brake override ---
    if brake_norm > 0.7:  # hard brake
        x = 0.0

    y = steer
    z = 0.0

    # --- Build and send UDP JSON packet ---
    msg = json.dumps({
        "x": round(x, 2),
        "y": round(y, 2),
        "z": z,
        "direction": direction
    })
    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

    # --- Debug output ---
    print(f"Dir: {direction:8s} | Gas: {gas_norm:.2f} | Brake: {brake_norm:.2f} | Steer: {y:.2f} | x={x:.2f}")

    time.sleep(0.02)  # 50 Hz
