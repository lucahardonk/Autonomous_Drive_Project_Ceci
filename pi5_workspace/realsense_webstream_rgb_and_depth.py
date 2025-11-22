#!/usr/bin/env python3
import cv2
import numpy as np
import pyrealsense2 as rs
from flask import Flask, Response

app = Flask(__name__)

# --- RealSense pipeline setup ---
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

pipeline.start(config)
print("✅ RealSense pipeline avviata")
print("🌐 Video RGB:  http://<IP>:8080/video")
print("🌐 Depth Map: http://<IP>:8080/depth")

def generate_rgb_frames():
    """RGB stream MJPEG"""
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def generate_depth_frames():
    """Depth map in scala di grigi (range completo RealSense)"""
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())

        # Normalizza per mappa in scala di grigi
        depth_normalized = cv2.normalize(depth_image, None, 0, 255,
                                         cv2.NORM_MINMAX)
        depth_gray = depth_normalized.astype(np.uint8)

        ret, buffer = cv2.imencode('.jpg', depth_gray)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_rgb_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/depth')
def depth_feed():
    return Response(generate_depth_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return (
        "<h2>🎥 RealSense Web Stream</h2>"
        "<p><a href='/video'>RGB Stream</a></p>"
        "<p><a href='/depth'>Depth Stream (Grayscale)</a></p>"
    )

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.stop()
        print("🛑 RealSense pipeline fermata")
