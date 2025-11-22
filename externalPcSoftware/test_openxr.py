import openvr
import time

openvr.init(openvr.VRApplication_Scene)
vr = openvr.VRSystem()

print("Ready! Move the sticks on your Quest controllers.\n")

while True:
    for device_index in range(openvr.k_unMaxTrackedDeviceCount):
        device_class = vr.getTrackedDeviceClass(device_index)

        # Check if it is a controller
        if device_class == openvr.TrackedDeviceClass_Controller:
            state = vr.getControllerState(device_index)
            if state[0]:  # state is valid

                # Thumbstick axes:
                x = state[1].rAxis[0].x
                y = state[1].rAxis[0].y

                # Trigger:
                trigger = state[1].rAxis[1].x

                print(f"Controller {device_index} | Stick: ({x:.3f}, {y:.3f}) | Trigger: {trigger:.3f}")

    time.sleep(0.01)
