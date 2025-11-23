import openvr
import time
import math

openvr.init(openvr.VRApplication_Scene)

vr = openvr.VRSystem()

print("="*80)
print("MEGA DEMO - Advanced OpenVR Controller Features")
print("="*80)
print("\nFeatures:")
print("  ✓ Position (X,Y,Z) and Velocity")
print("  ✓ Rotation (RPY + Quaternion) and Angular Velocity")
print("  ✓ Buttons: Pressed + Touched (capacitive)")
print("  ✓ Button Events: Press/Release detection")
print("  ✓ Axes: Thumbstick, Trigger, Grip")
print("  ✓ Tracking Quality monitoring")
print("  ✓ Battery Level and charging status")
print("  ✓ Haptic Patterns (different for each button)")
print("  ✓ Device Information\n")

# Button bit masks for Quest/Oculus Touch controllers
BUTTON_SYSTEM = (1 << openvr.k_EButton_System)
BUTTON_MENU = (1 << openvr.k_EButton_ApplicationMenu)
BUTTON_GRIP = (1 << openvr.k_EButton_Grip)
BUTTON_A = (1 << openvr.k_EButton_A)
BUTTON_THUMBSTICK = (1 << openvr.k_EButton_SteamVR_Touchpad)
BUTTON_TRIGGER = (1 << openvr.k_EButton_SteamVR_Trigger)

# Axis indices
AXIS_THUMBSTICK = 0
AXIS_TRIGGER = 1
AXIS_GRIP = 2

# Button tracker for events
class ButtonTracker:
    def __init__(self):
        self.prev_state = {}
    
    def check_events(self, device_index, current_buttons):
        """Detect button press/release events"""
        prev = self.prev_state.get(device_index, 0)
        
        # Just pressed (wasn't pressed before, is now)
        pressed = (current_buttons & ~prev)
        
        # Just released (was pressed before, isn't now)
        released = (prev & ~current_buttons)
        
        self.prev_state[device_index] = current_buttons
        
        events = []
        if pressed & BUTTON_A:
            events.append("A_PRESSED")
        if released & BUTTON_A:
            events.append("A_RELEASED")
        if pressed & BUTTON_GRIP:
            events.append("GRIP_PRESSED")
        if released & BUTTON_GRIP:
            events.append("GRIP_RELEASED")
        if pressed & BUTTON_THUMBSTICK:
            events.append("STICK_PRESSED")
        if released & BUTTON_THUMBSTICK:
            events.append("STICK_RELEASED")
        if pressed & BUTTON_TRIGGER:
            events.append("TRIG_PRESSED")
        if released & BUTTON_TRIGGER:
            events.append("TRIG_RELEASED")
        if pressed & BUTTON_MENU:
            events.append("MENU_PRESSED")
        if released & BUTTON_MENU:
            events.append("MENU_RELEASED")
        
        return events

button_tracker = ButtonTracker()

def get_controller_role_name(device_index):
    """Get whether controller is left or right hand"""
    role = vr.getControllerRoleForTrackedDeviceIndex(device_index)
    if role == openvr.TrackedControllerRole_LeftHand:
        return "LEFT "
    elif role == openvr.TrackedControllerRole_RightHand:
        return "RIGHT"
    else:
        return "UNKN "

def get_controller_role(device_index):
    """Get controller role enum"""
    return vr.getControllerRoleForTrackedDeviceIndex(device_index)

def matrix_to_euler(matrix):
    """Convert rotation matrix to Euler angles (Roll, Pitch, Yaw) in degrees"""
    r00, r01, r02 = matrix[0][0], matrix[0][1], matrix[0][2]
    r10, r11, r12 = matrix[1][0], matrix[1][1], matrix[1][2]
    r20, r21, r22 = matrix[2][0], matrix[2][1], matrix[2][2]
    
    pitch = math.asin(-r20)
    
    if math.cos(pitch) > 0.001:
        roll = math.atan2(r21, r22)
        yaw = math.atan2(r10, r00)
    else:
        roll = math.atan2(-r12, r11)
        yaw = 0
    
    roll_deg = math.degrees(roll)
    pitch_deg = math.degrees(pitch)
    yaw_deg = math.degrees(yaw)
    
    return roll_deg, pitch_deg, yaw_deg

def matrix_to_quaternion(matrix):
    """Convert rotation matrix to quaternion (w, x, y, z)"""
    r00, r01, r02 = matrix[0][0], matrix[0][1], matrix[0][2]
    r10, r11, r12 = matrix[1][0], matrix[1][1], matrix[1][2]
    r20, r21, r22 = matrix[2][0], matrix[2][1], matrix[2][2]
    
    trace = r00 + r11 + r22
    
    if trace > 0:
        s = 0.5 / math.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (r21 - r12) * s
        y = (r02 - r20) * s
        z = (r10 - r01) * s
    elif r00 > r11 and r00 > r22:
        s = 2.0 * math.sqrt(1.0 + r00 - r11 - r22)
        w = (r21 - r12) / s
        x = 0.25 * s
        y = (r01 + r10) / s
        z = (r02 + r20) / s
    elif r11 > r22:
        s = 2.0 * math.sqrt(1.0 + r11 - r00 - r22)
        w = (r02 - r20) / s
        x = (r01 + r10) / s
        y = 0.25 * s
        z = (r12 + r21) / s
    else:
        s = 2.0 * math.sqrt(1.0 + r22 - r00 - r11)
        w = (r10 - r01) / s
        x = (r02 + r20) / s
        y = (r12 + r21) / s
        z = 0.25 * s
    
    return w, x, y, z

def print_button_state(buttons_pressed):
    """Decode and print button pressed states"""
    states = []
    
    if buttons_pressed & BUTTON_A:
        states.append("A")
    if buttons_pressed & BUTTON_GRIP:
        states.append("Grip")
    if buttons_pressed & BUTTON_THUMBSTICK:
        states.append("Stick")
    if buttons_pressed & BUTTON_TRIGGER:
        states.append("Trig")
    if buttons_pressed & BUTTON_MENU:
        states.append("Menu")
    
    return f"Pressed:[{', '.join(states) if states else 'none'}]"

def print_touch_state(buttons_touched):
    """Decode and print capacitive touch states"""
    touches = []
    
    if buttons_touched & BUTTON_A:
        touches.append("A")
    if buttons_touched & BUTTON_THUMBSTICK:
        touches.append("Stick")
    if buttons_touched & BUTTON_TRIGGER:
        touches.append("Trig")
    if buttons_touched & BUTTON_GRIP:
        touches.append("Grip")
    
    return f"Touched:[{', '.join(touches) if touches else 'none'}]"

def get_tracking_result(device_index):
    """Get tracking quality/status"""
    poses = vr.getDeviceToAbsoluteTrackingPose(
        openvr.TrackingUniverseStanding, 
        0,
        openvr.k_unMaxTrackedDeviceCount
    )
    
    pose = poses[device_index]
    
    tracking_results = {
        200: "Uninitialized",
        100: "Calibrating_InProgress",
        101: "Calibrating_OutOfRange",
        1: "Running_OK",
        2: "Running_OutOfRange",
        3: "Fallback_RotationOnly",
    }
    
    result = pose.eTrackingResult
    status = tracking_results.get(result, f"Unknown({result})")
    
    return status

def get_battery_level(device_index):
    """Get battery percentage and charging status"""
    try:
        battery = vr.getFloatTrackedDeviceProperty(
            device_index, 
            openvr.Prop_DeviceBatteryPercentage_Float
        )
        
        is_charging = vr.getBoolTrackedDeviceProperty(
            device_index,
            openvr.Prop_DeviceIsCharging_Bool
        )
        
        status = "⚡" if is_charging else ""
        return f"{battery*100:.0f}%{status}"
    except:
        return "N/A"

def get_device_info(device_index):
    """Get controller model, serial, manufacturer"""
    try:
        model = vr.getStringTrackedDeviceProperty(
            device_index,
            openvr.Prop_ModelNumber_String
        )
        
        serial = vr.getStringTrackedDeviceProperty(
            device_index,
            openvr.Prop_SerialNumber_String
        )
        
        manufacturer = vr.getStringTrackedDeviceProperty(
            device_index,
            openvr.Prop_ManufacturerName_String
        )
        
        return f"{manufacturer} {model} (S/N: {serial})"
    except:
        return "Unknown Device"

def get_velocity_data(device_index):
    """Get linear and angular velocity"""
    poses = vr.getDeviceToAbsoluteTrackingPose(
        openvr.TrackingUniverseStanding, 
        0,
        openvr.k_unMaxTrackedDeviceCount
    )
    
    pose = poses[device_index]
    
    if pose.bPoseIsValid:
        # Linear velocity (m/s)
        vel_x = pose.vVelocity[0]
        vel_y = pose.vVelocity[1]
        vel_z = pose.vVelocity[2]
        
        # Angular velocity (rad/s)
        ang_x = pose.vAngularVelocity[0]
        ang_y = pose.vAngularVelocity[1]
        ang_z = pose.vAngularVelocity[2]
        
        return (vel_x, vel_y, vel_z), (ang_x, ang_y, ang_z)
    return (0, 0, 0), (0, 0, 0)

def get_pose_data(device_index):
    """Get controller pose (position and rotation)"""
    poses = vr.getDeviceToAbsoluteTrackingPose(
        openvr.TrackingUniverseStanding, 
        0,
        openvr.k_unMaxTrackedDeviceCount
    )
    
    pose = poses[device_index]
    
    if pose.bPoseIsValid:
        matrix = pose.mDeviceToAbsoluteTracking
        pos_x = matrix[0][3]
        pos_y = matrix[1][3]
        pos_z = matrix[2][3]
        
        roll, pitch, yaw = matrix_to_euler(matrix)
        qw, qx, qy, qz = matrix_to_quaternion(matrix)
        
        return (pos_x, pos_y, pos_z), (roll, pitch, yaw), (qw, qx, qy, qz), True
    else:
        return (0, 0, 0), (0, 0, 0), (0, 0, 0, 0), False

def trigger_haptic_pattern(device_index, pattern="short"):
    """Trigger different haptic patterns"""
    if pattern == "short":
        # Quick pulse
        vr.triggerHapticPulse(device_index, 0, 3000)
    elif pattern == "double":
        # Double tap
        vr.triggerHapticPulse(device_index, 0, 2000)
        time.sleep(0.05)
        vr.triggerHapticPulse(device_index, 0, 2000)
    elif pattern == "long":
        # Long vibration
        vr.triggerHapticPulse(device_index, 0, 500000)
    elif pattern == "buzz":
        # Buzzing pattern
        for i in range(3):
            vr.triggerHapticPulse(device_index, 0, 2000)
            time.sleep(0.03)

def process_controller(device_index, role_name):
    """Process and print all data for a single controller"""
    state = vr.getControllerState(device_index)
    
    if state[0]:  # state is valid
        controller_state = state[1]
        
        # Buttons
        buttons_pressed = controller_state.ulButtonPressed
        buttons_touched = controller_state.ulButtonTouched
        button_str = print_button_state(buttons_pressed)
        touch_str = print_touch_state(buttons_touched)
        
        # Button events
        events = button_tracker.check_events(device_index, buttons_pressed)
        event_str = f"Events:[{', '.join(events) if events else 'none'}]"
        
        # Axes
        thumbstick_x = controller_state.rAxis[AXIS_THUMBSTICK].x
        thumbstick_y = controller_state.rAxis[AXIS_THUMBSTICK].y
        trigger_val = controller_state.rAxis[AXIS_TRIGGER].x
        
        grip_val = 0.0
        if len(controller_state.rAxis) > AXIS_GRIP:
            grip_val = controller_state.rAxis[AXIS_GRIP].x
        
        # Pose
        pos, rpy, quat, pose_valid = get_pose_data(device_index)
        
        # Velocity
        lin_vel, ang_vel = get_velocity_data(device_index)
        
        # Tracking and battery
        tracking = get_tracking_result(device_index)
        battery = get_battery_level(device_index)
        
        # Print everything (multi-line for readability)
        print(f"{role_name} [{device_index}] | {button_str} {touch_str} | {event_str}")
        print(f"          | Stick:({thumbstick_x:6.3f},{thumbstick_y:6.3f}) "
              f"Trig:{trigger_val:.3f} Grip:{grip_val:.3f}")
        
        if pose_valid:
            print(f"          | Pos:({pos[0]:6.3f},{pos[1]:6.3f},{pos[2]:6.3f}) "
                  f"Vel:({lin_vel[0]:5.2f},{lin_vel[1]:5.2f},{lin_vel[2]:5.2f})m/s")
            print(f"          | RPY:({rpy[0]:6.1f}°,{rpy[1]:6.1f}°,{rpy[2]:6.1f}°) "
                  f"AngVel:({ang_vel[0]:5.2f},{ang_vel[1]:5.2f},{ang_vel[2]:5.2f})rad/s")
            print(f"          | Quat:({quat[0]:.3f},{quat[1]:6.3f},{quat[2]:6.3f},{quat[3]:6.3f})")
        else:
            print(f"          | Pose: INVALID")
        
        print(f"          | Tracking:{tracking} Battery:{battery}")
        
        # Haptic feedback based on button events
        haptic_triggered = False
        for event in events:
            if "A_PRESSED" in event:
                trigger_haptic_pattern(device_index, "short")
                print(f"  → Haptic: SHORT pulse (A pressed)")
                haptic_triggered = True
            elif "GRIP_PRESSED" in event:
                trigger_haptic_pattern(device_index, "double")
                print(f"  → Haptic: DOUBLE tap (Grip pressed)")
                haptic_triggered = True
            elif "STICK_PRESSED" in event:
                trigger_haptic_pattern(device_index, "buzz")
                print(f"  → Haptic: BUZZ pattern (Stick pressed)")
                haptic_triggered = True
            elif "TRIG_PRESSED" in event:
                trigger_haptic_pattern(device_index, "long")
                print(f"  → Haptic: LONG vibration (Trigger pressed)")
                haptic_triggered = True
        
        return True
    return False

def print_left(left_controller_index):
    """Print left controller data"""
    if left_controller_index is not None:
        return process_controller(left_controller_index, "LEFT ")
    return False

def print_right(right_controller_index):
    """Print right controller data"""
    if right_controller_index is not None:
        return process_controller(right_controller_index, "RIGHT")
    return False

# Find left and right controller indices
left_controller_index = None
right_controller_index = None

for device_index in range(openvr.k_unMaxTrackedDeviceCount):
    device_class = vr.getTrackedDeviceClass(device_index)
    if device_class == openvr.TrackedDeviceClass_Controller:
        role = get_controller_role(device_index)
        if role == openvr.TrackedControllerRole_LeftHand:
            left_controller_index = device_index
            print(f"LEFT Controller [{device_index}]: {get_device_info(device_index)}")
        elif role == openvr.TrackedControllerRole_RightHand:
            right_controller_index = device_index
            print(f"RIGHT Controller [{device_index}]: {get_device_info(device_index)}")

print(f"\nFound controllers - Left: {left_controller_index}, Right: {right_controller_index}")
print("="*80)
print("\nStarting main loop...\n")

# Main loop
while True:
    # Process LEFT controller - comment this line to disable left
    print_left(left_controller_index)
    
    print()  # Blank line between left and right
    
    # Process RIGHT controller - comment this line to disable right
    print_right(right_controller_index)
    
    print("\n" + "="*80 + "\n")  # Separator between frames
    
    time.sleep(0.1)  # 10Hz update rate