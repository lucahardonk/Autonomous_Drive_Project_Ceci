import pygame

# Initialize pygame and joystick module
pygame.init()
pygame.joystick.init()

# Open the first joystick (check with pygame.joystick.get_count())
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Detected: {joystick.get_name()}")
print(f"Axes: {joystick.get_numaxes()}, Buttons: {joystick.get_numbuttons()}")

try:
    while True:
        pygame.event.pump()  # process internal events

        # Read all axis values
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        print(f"Axes: {axes}")
        print(f"Buttons: {buttons}")

except KeyboardInterrupt:
    print("Exiting...")
    pygame.quit()
