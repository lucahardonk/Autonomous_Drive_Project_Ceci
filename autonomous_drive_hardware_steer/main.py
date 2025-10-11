import socket, json, pygame, time

# === Network configuration ===
UDP_IP = "172.20.10.10" #UDP_IP = "192.168.1.162"   # IP address of the Arduino R4 WiFi
UDP_PORT = 8888            # UDP port number used for communication

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === Initialize joystick ===
pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

print(f"🎮 Sending joystick data to {UDP_IP}:{UDP_PORT} at 50 Hz")

# === State variables ===
direction = 0               # -1 = BACKWARD, 0 = NEUTRO, 1 = FORWARD
forward_prev = 0            # Previous state of the forward button
backward_prev = 0           # Previous state of the backward button

# === Main loop ===
while True:
    pygame.event.pump()

    # --- Read joystick inputs ---
    steer = j.get_axis(0)       # Axis 0: steering (-1 = left, +1 = right)
    gas = j.get_axis(5)         # Axis 5: gas pedal (-1 = not pressed, +1 = fully pressed)
    brake = j.get_axis(2)       # Axis 2: brake pedal (-1 = not pressed, +1 = fully pressed)
    forward = j.get_button(5)   # Button 5: toggle forward/neutral
    backward = j.get_button(4)  # Button 4: toggle backward/neutral

    # --- Detect button press (edge detection) ---
    if forward and not forward_prev:
        if direction == -1:
            direction = 0       # BACKWARD → NEUTRO
        elif direction == 0:
            direction = 1       # NEUTRO → FORWARD
        # If already FORWARD, stay FORWARD

    if backward and not backward_prev:
        if direction == 1:
            direction = 0       # FORWARD → NEUTRO
        elif direction == 0:
            direction = -1      # NEUTRO → BACKWARD
        # If already BACKWARD, stay BACKWARD

    # Save button states
    forward_prev = forward
    backward_prev = backward

    # --- Normalize pedals ---
    gas_norm = (gas + 1) / 2
    brake_norm = (brake + 1) / 2

    # --- Compute movement ---
    if gas_norm > 0.05:
        x = gas_norm * direction
    else:
        x = 0.0

    # --- Apply brake override ---
    if brake_norm > 0.7:
        x = 0.0

    # --- Steering axis ---
    y = steer                  # -1 = full left, +1 = full right
    z = 0.0                    # Reserved / unused

    # --- Build and send UDP packet ---
    msg = json.dumps({
        "x": round(x, 2),       # Speed scaled by direction
        "y": round(y, 2),       # Steering (-1 to +1)
        "z": z,
        "direction": direction
    })
    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

    # --- Debug output ---
    dir_str = { -1: "BACKWARD", 0: "NEUTRO", 1: "FORWARD" }[direction]
    print(f"Dir: {dir_str:8s} ({direction}) | Gas: {gas_norm:.2f} | Brake: {brake_norm:.2f} | "
          f"Steer (y): {y:.2f} | x={x:.2f}")

    time.sleep(0.02)
