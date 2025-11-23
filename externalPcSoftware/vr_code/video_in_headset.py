import openvr
import cv2
import time
import os
import threading
import requests
import json

class ControllerMonitor:
    def __init__(self, vr_system):
        self.vr_system = vr_system
        self.right_controller_index = None
        self.joystick_x = 0.0
        self.joystick_y = 0.0
        self.buttons_pressed = 0
        self.buttons_touched = 0
        self.trigger_value = 0.0
        self.running = False
        self.thread = None
        
    def find_right_controller(self):
        """Find the device index of the right controller"""
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            device_class = self.vr_system.getTrackedDeviceClass(i)
            if device_class == openvr.TrackedDeviceClass_Controller:
                role = self.vr_system.getControllerRoleForTrackedDeviceIndex(i)
                if role == openvr.TrackedControllerRole_RightHand:
                    return i
        return None
    
    def update_controller_state(self):
        """Continuously update controller state"""
        while self.running:
            if self.right_controller_index is not None:
                result, state = self.vr_system.getControllerState(self.right_controller_index)
                if result:
                    # Joystick values (axis 0)
                    self.joystick_x = state.rAxis[0].x
                    self.joystick_y = state.rAxis[0].y
                    
                    # Trigger value (axis 1)
                    self.trigger_value = state.rAxis[1].x
                    
                    # Button states
                    self.buttons_pressed = state.ulButtonPressed
                    self.buttons_touched = state.ulButtonTouched
            
            time.sleep(0.01)  # Update at ~100Hz
    
    def start(self):
        """Start monitoring controller"""
        self.right_controller_index = self.find_right_controller()
        if self.right_controller_index is not None:
            print(f"Right controller found at index: {self.right_controller_index}")
            self.running = True
            self.thread = threading.Thread(target=self.update_controller_state, daemon=True)
            self.thread.start()
            return True
        else:
            print("WARNING: Right controller not found!")
            return False
    
    def stop(self):
        """Stop monitoring controller"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def get_joystick(self):
        """Get current joystick values"""
        return self.joystick_x, self.joystick_y
    
    def get_trigger(self):
        """Get current trigger value"""
        return self.trigger_value
    
    def is_button_pressed(self, button_id):
        """Check if a specific button is pressed"""
        return bool(self.buttons_pressed & (1 << button_id))
    
    def is_button_touched(self, button_id):
        """Check if a specific button is touched"""
        return bool(self.buttons_touched & (1 << button_id))
    
    def print_state(self):
        """Print current controller state"""
        print(f"\rJoystick: X={self.joystick_x:+.3f} Y={self.joystick_y:+.3f} | "
              f"Trigger: {self.trigger_value:.3f} | "
              f"Pressed: {self.buttons_pressed:>3} | "
              f"Touched: {self.buttons_touched:>3}", end="")


class CommandPublisher:
    def __init__(self, base_url="http://192.168.1.149:5000"):
        self.base_url = base_url
        self.cmd_url = f"{base_url}/cmd"
        self.session = requests.Session()
        self.last_command = None
        
    def publish_command(self, motor_left_pwm=0, motor_right_pwm=0, direction=1, steer_angle=0):
        """
        Publish command to the robot
        
        Args:
            motor_left_pwm: Left motor PWM (0-255)
            motor_right_pwm: Right motor PWM (0-255)
            direction: Direction (1=forward, 0=backward)
            steer_angle: Steering angle in degrees (-30 to +30)
        """
        # Clamp steer angle to valid range
        steer_angle = max(-30, min(30, steer_angle))
        
        command = {
            "cmd": {
                "motorLeftPwm": int(motor_left_pwm),
                "motorRightPwm": int(motor_right_pwm),
                "direction": int(direction),
                "steerAngle": int(steer_angle)
            }
        }
        
        try:
            response = self.session.post(
                self.cmd_url,
                json=command,
                timeout=0.1  # Short timeout to avoid blocking
            )
            
            if response.status_code == 200:
                self.last_command = command
                return True
            else:
                print(f"\nWarning: Command failed with status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            # Timeout is acceptable for real-time control
            return True
        except Exception as e:
            print(f"\nError publishing command: {e}")
            return False
    
    def get_last_command(self):
        """Get the last published command"""
        return self.last_command


print("Initializing OpenVR Overlay System...")

# Initialize OpenVR in overlay mode
openvr.init(openvr.VRApplication_Overlay)
overlay_system = openvr.VROverlay()
vr_system = openvr.VRSystem()

# Initialize controller monitor
controller = ControllerMonitor(vr_system)
controller.start()

# Initialize command publisher
publisher = CommandPublisher()

print("Creating overlay...")
overlay_key = "video.stream.overlay"
overlay_name = "Video Stream Overlay"
overlay_handle = overlay_system.createOverlay(overlay_key, overlay_name)

print(f"Overlay created with handle: {overlay_handle}")

# Set overlay position
transform = openvr.HmdMatrix34_t()
transform.m[0][0] = 1.0
transform.m[1][1] = 1.0
transform.m[2][2] = 1.0
transform.m[0][3] = 0.0   # X
transform.m[1][3] = 1.5   # Y (altezza)
transform.m[2][3] = -2.0  # Z (distanza)

overlay_system.setOverlayTransformAbsolute(
    overlay_handle,
    openvr.TrackingUniverseStanding,
    transform
)

overlay_system.setOverlayWidthInMeters(overlay_handle, 2.0)
overlay_system.showOverlay(overlay_handle)

print("Overlay visible in VR!")

# Apri lo stream video
video_url = "http://192.168.1.149:8080/video"
cap = cv2.VideoCapture(video_url)

if not cap.isOpened():
    print("ERROR: Cannot open video stream!")
    controller.stop()
    openvr.shutdown()
    exit(1)

print("Video stream opened successfully")
print("Press Ctrl+C to stop\n")

# File temporaneo per i frame
temp_frame_path = os.path.abspath("temp_frame.jpg")

try:
    frame_count = 0
    last_print_time = time.time()
    last_command_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("\nFailed to read frame, reconnecting...")
            cap.release()
            time.sleep(1)
            cap = cv2.VideoCapture(video_url)
            continue
        
        # Salva il frame come JPEG temporaneo
        cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        # Aggiorna l'overlay con il nuovo frame
        overlay_system.setOverlayFromFile(overlay_handle, temp_frame_path)
        
        # Get controller values
        joy_x, joy_y = controller.get_joystick()
        trigger = controller.get_trigger()
        
        # Calculate steering angle from joystick X (-1 to +1 -> -30 to +30 degrees)
        steer_angle = joy_x * 30
        # Calculate motor PWM from trigger (0 to 1 -> 0 to 255)
        motor_pwm = int(trigger * 255)

        # Check grip button for direction  
        grip_pressed = controller.is_button_pressed(openvr.k_EButton_Grip)  
        direction = -1 if grip_pressed else 1
       
        
        # Publish command at 20Hz (every 0.05 seconds)
        current_time = time.time()
        if current_time - last_command_time >= 0.01:
            publisher.publish_command(
                motor_left_pwm=motor_pwm,
                motor_right_pwm=motor_pwm,
                direction=direction,
                steer_angle=steer_angle
            )
            last_command_time = current_time
        
        # Print controller state in real-time (every 0.1 seconds)
        if current_time - last_print_time >= 0.1:
            print(f"\rJoystick: X={joy_x:+.3f} Y={joy_y:+.3f} | "  
                f"Steer: {steer_angle:+6.1f}° | "  
                f"Motor: {motor_pwm:3d} | "  
                f"Dir: {direction:+2d} | "  
                f"Grip: {'YES' if grip_pressed else 'NO '}", end="")
            last_print_time = current_time
        
        frame_count += 1
        
        # Piccolo delay (~30 FPS per non sovraccaricare il disco)
        time.sleep(0.008)

except KeyboardInterrupt:
    print("\n\nShutting down...")
    # Send stop command
    publisher.publish_command(0, 0, 1, 0)

finally:
    controller.stop()
    cap.release()
    
    # Rimuovi file temporaneo
    if os.path.exists(temp_frame_path):
        os.remove(temp_frame_path)
    
    overlay_system.destroyOverlay(overlay_handle)
    openvr.shutdown()
    print("Cleanup complete")