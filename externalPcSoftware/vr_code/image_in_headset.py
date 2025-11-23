import openvr
import time
import os

print("Initializing OpenVR Overlay System...")

# Initialize OpenVR in overlay mode
openvr.init(openvr.VRApplication_Overlay)

# Get overlay interface
overlay_system = openvr.VROverlay()

print("Creating overlay...")

# Create overlay
overlay_key = "test.image.overlay"
overlay_name = "Test Image Overlay"
overlay_handle = overlay_system.createOverlay(overlay_key, overlay_name)

print(f"Overlay created with handle: {overlay_handle}")

# Load your test image
image_path = "test_image.jpg"  # PUT YOUR IMAGE FILE NAME HERE

# Get absolute path
abs_image_path = os.path.abspath(image_path)
print(f"Loading image: {abs_image_path}")

# Set overlay position (floating in front of user)
transform = openvr.HmdMatrix34_t()
transform.m[0][0] = 1.0
transform.m[0][1] = 0.0
transform.m[0][2] = 0.0
transform.m[0][3] = 0.0  # X position

transform.m[1][0] = 0.0
transform.m[1][1] = 1.0
transform.m[1][2] = 0.0
transform.m[1][3] = 1.5  # Y position (1.5m high)

transform.m[2][0] = 0.0
transform.m[2][1] = 0.0
transform.m[2][2] = 1.0
transform.m[2][3] = -1.5  # Z position (1.5m forward)

overlay_system.setOverlayTransformAbsolute(
    overlay_handle, 
    openvr.TrackingUniverseStanding, 
    transform
)

print("Overlay positioned in space")

# Set overlay width (in meters) - 1 meter wide
overlay_system.setOverlayWidthInMeters(overlay_handle, 1.0)

print("Overlay size set to 1.0 meters")

# Upload image texture from file (much simpler!)
print("Uploading image texture...")
overlay_system.setOverlayFromFile(overlay_handle, abs_image_path)

print("Texture uploaded")

# Show the overlay
overlay_system.showOverlay(overlay_handle)

print("\n" + "="*60)
print("✓ Overlay is now visible in VR!")
print("="*60)
print("\nInstructions:")
print("  - Put on your headset")
print("  - Look around - you should see the image floating in space")
print("  - The image is positioned 1.5m forward and 1.5m up")
print("  - Press Ctrl+C in this terminal to close the overlay")
print("\nKeeping overlay alive...")

try:
    # Keep the script running
    while True:
        time.sleep(1)
        
        # Optional: Check if overlay is still valid
        if not overlay_system.isOverlayVisible(overlay_handle):
            print("Overlay became invisible, showing again...")
            overlay_system.showOverlay(overlay_handle)
            
except KeyboardInterrupt:
    print("\n\nShutting down overlay...")
    overlay_system.destroyOverlay(overlay_handle)
    openvr.shutdown()
    print("Overlay closed. Done!")