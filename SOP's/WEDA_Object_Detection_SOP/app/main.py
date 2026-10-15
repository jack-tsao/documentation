import time
import numpy as np
import cv2
import pyrealsense2 as rs
from ultralytics import YOLO

MODEL_PATH = "yolov8n-seg.pt"
STREAM_WIDTH = 640
STREAM_HEIGHT = 480
STREAM_FPS = 30

# Leave as None to track all 80 COCO classes, or set e.g. {"person"} to filter.
TRACKED_CLASSES = None

CLASS_COLORS = {}


def list_devices():
    ctx = rs.context()
    return [
        (d.get_info(rs.camera_info.name), d.get_info(rs.camera_info.serial_number))
        for d in ctx.query_devices()
    ]


def select_device():
    devices = list_devices()
    if not devices:
        raise RuntimeError("No RealSense device found. Check the USB connection.")

    if len(devices) == 1:
        name, serial = devices[0]
        print(f"Using {name} ({serial})")
        return serial

    print("Multiple RealSense devices found:")
    for i, (name, serial) in enumerate(devices):
        print(f"  [{i}] {name} ({serial})")
    choice = input("Select a camera index: ").strip()
    return devices[int(choice)][1]


def start_pipeline(serial):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(serial)
    config.enable_stream(rs.stream.color, STREAM_WIDTH, STREAM_HEIGHT, rs.format.bgr8, STREAM_FPS)
    config.enable_stream(rs.stream.depth, STREAM_WIDTH, STREAM_HEIGHT, rs.format.z16, STREAM_FPS)
    profile = pipeline.start(config)

    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
    align = rs.align(rs.stream.color)
    return pipeline, align, depth_scale


def mask_distance_m(depth_image, mask_full, depth_scale):
    ys, xs = np.where(mask_full)
    if len(xs) == 0:
        return None
    depths = depth_image[ys, xs].astype(np.float32) * depth_scale
    depths = depths[depths > 0]
    if len(depths) == 0:
        return None
    return float(np.median(depths))


def color_for_class(cls_id):
    if cls_id not in CLASS_COLORS:
        rng = np.random.default_rng(cls_id)
        CLASS_COLORS[cls_id] = rng.integers(60, 255, 3).tolist()
    return CLASS_COLORS[cls_id]


def draw_details_panel(frame, detections, fps):
    panel_w = 230
    h, w = frame.shape[:2]
    panel = np.zeros((h, panel_w, 3), dtype=np.uint8)

    cv2.putText(panel, f"FPS: {fps:.1f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(panel, f"Objects: {len(detections)}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.line(panel, (10, 60), (panel_w - 10, 60), (80, 80, 80), 1)

    y = 85
    for det in detections:
        dist_str = f"{det['distance_m']:.2f}m" if det["distance_m"] is not None else "--"
        line1 = f"{det['class']}"
        line2 = f"  {det['confidence']:.0%}  {dist_str}"
        cv2.putText(panel, line1, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, det["color"], 1, cv2.LINE_AA)
        cv2.putText(panel, line2, (10, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
        y += 42
        if y > h - 20:
            break

    return np.hstack([frame, panel])


def run(serial):
    pipeline, align, depth_scale = start_pipeline(serial)
    model = YOLO(MODEL_PATH)

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            results = model(color_image, verbose=False)[0]
            overlay = color_image.copy()
            detections = []

            if results.masks is not None:
                for i, mask_data in enumerate(results.masks.data):
                    cls_id = int(results.boxes.cls[i])
                    cls_name = model.names[cls_id]
                    if TRACKED_CLASSES and cls_name not in TRACKED_CLASSES:
                        continue

                    conf = float(results.boxes.conf[i])
                    mask = mask_data.cpu().numpy().astype(np.uint8)
                    mask_full = cv2.resize(mask, (STREAM_WIDTH, STREAM_HEIGHT)).astype(bool)

                    color = color_for_class(cls_id)
                    overlay[mask_full] = (overlay[mask_full] * 0.5 + np.array(color) * 0.5).astype(np.uint8)

                    dist = mask_distance_m(depth_image, mask_full, depth_scale)

                    ys, xs = np.where(mask_full)
                    x0, y0 = int(xs.min()), int(ys.min())
                    label = f"{cls_name} {conf:.0%}"
                    if dist is not None:
                        label += f" {dist:.2f}m"
                    cv2.putText(overlay, label, (x0, max(y0 - 6, 12)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                    detections.append({
                        "class": cls_name,
                        "confidence": conf,
                        "distance_m": dist,
                        "color": color,
                    })

            now = time.time()
            fps = 1.0 / max(now - prev_time, 1e-6)
            prev_time = now

            display_frame = draw_details_panel(overlay, detections, fps)
            cv2.imshow("RealSense Object Detection", display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    selected_serial = select_device()
    run(selected_serial)
