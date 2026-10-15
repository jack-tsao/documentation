# RealSense Object Detection + Depth — WEDA Demo

**Status: Test / Prototype.** Built as a proof-of-concept for running a real computer
vision workload through WEDA's deployment pipeline on an Advantech ARK-2252.

**Author:** Max Langs (AJP intern)

## What it does

- Lists connected Intel RealSense devices on launch; auto-selects if only one is found.
- Runs **YOLOv8-seg** on the RealSense color stream for pixel-level object **segmentation
  masks** (not bounding boxes) — the actual silhouette of each detected object is
  highlighted.
- Aligns the RealSense depth stream to the color stream and samples depth under each
  mask to report a **live distance (meters)** per detected object, using the camera's
  stereo depth sensors.
- Shows a live details panel (FPS, object count, class/confidence/distance per object)
  rendered next to the video feed.
- Tracks all 80 COCO classes by default (`TRACKED_CLASSES = None` in `main.py`); set it
  to e.g. `{"person"}` to filter to a single class.

## Architecture

```
RealSense camera (RGB + depth, 4 sensors: left/right IR, RGB, IR projector)
        │
        ▼
main.py (Python)
  ├─ pyrealsense2 — pulls aligned RGB + depth frames
  ├─ ultralytics YOLOv8-seg — segmentation masks on the RGB frame (CPU-only PyTorch;
  │  the ARK-2252 is Intel, no NVIDIA GPU, so CUDA builds are intentionally avoided)
  ├─ depth sampling — median depth under each mask → per-object distance
  └─ OpenCV (cv2.imshow) — renders the live window + details panel
        │
        ▼
Docker image (m4x1m25/weda-object-detection)
        │
        ▼
Docker Hub (registry)
        │
        ▼
WEDA Console → Container Stack → deployed to ARK-2252 device
```

## Running it locally (outside WEDA, for development)

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
Press `q` in the video window to quit. First run auto-downloads `yolov8n-seg.pt`.

## How this runs through WEDA

This is the actual deployment pipeline used to get it running on the ARK-2252:

1. **Build the image** (on a dev machine with Docker):
   ```bash
   docker build -t m4x1m25/weda-object-detection:v2 .
   ```
2. **Push to a registry** (Docker Hub):
   ```bash
   docker push m4x1m25/weda-object-detection:v2
   ```
3. **Register the registry in WEDA Console** — Registries → Add → Docker Hub, with
   a username + access token (Read & Write scope needed for push; a push-capable
   token works for pull too).
4. **Create a Container Stack in WEDA Console** — upload `docker-compose.yml` from
   this repo, which defines the service, required device/volume mounts, and restart
   policy.
5. **Deploy the stack to the target device** (WEDA Console → Devices → [device] →
   Deployments → + Deploy).
6. **One manual step still required on the device itself**: run `xhost +local:docker`
   once per boot so the container's GUI window is allowed to display on the device's
   X11 session. (This is a device-level X11 permission, not something WEDA manages.)

## docker-compose.yml, annotated

```yaml
services:
  object-detection:
    image: m4x1m25/weda-object-detection:v2
    privileged: true              # needed for RealSense USB enumeration
    environment:
      - DISPLAY=:0                # the device's X11 display
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix   # lets the container open a window on the host display
      - /dev/bus/usb:/dev/bus/usb       # RealSense camera access
    devices:
      - /dev/dri:/dev/dri         # GPU device passthrough (hardware-accelerated rendering)
    restart: unless-stopped
```

## Known issues / lessons learned (worth reading before touching this again)

- **Qt/xcb crash (fixed in v2).** v1 of this image crash-looped indefinitely
  (`Restarting (139)`, i.e. segfault) because `opencv-python`'s GUI backend (Qt) needs
  several `libxcb-*` system libraries that a minimal Ubuntu base image doesn't include.
  WEDA's dashboard showed this as a stuck "Deploying" status rather than a clear error,
  which made it look like a pull/network problem — it wasn't. If you see "Deploying"
  that never resolves, **check `docker ps -a` and `docker logs` directly on the device**
  rather than trusting the Console status alone.
- **CPU-only PyTorch is intentional.** `requirements.txt` pins
  `--extra-index-url https://download.pytorch.org/whl/cpu` — without this, `ultralytics`
  pulls the full CUDA build of PyTorch (multi-GB, useless on this hardware since the
  ARK-2252 has no NVIDIA GPU).
- **This image only works on the ARK-2252** (x86_64/Intel). It will **not** run on the
  AIR-055 (Qualcomm/ARM) — that would need a separate build using Qualcomm's QNN/SNPE
  toolchain instead of PyTorch.
- **Docker Hub login is per-user, not per-session.** `docker build`/`push` run as root
  via `sudo` need their own `docker login` — being logged in as your normal user isn't
  enough.

## Not yet implemented (next steps)

- **WEDA telemetry** — publishing detection results (counts, classes, confidence) to
  WEDA Core via the WEDA SubNode SDK, so detection data is visible from the Console's
  Telemetry tab instead of only on the device's own screen.
- **WEDA notifications/alerts** — triggering a WEDA alert policy on specific detection
  events.
- **AIR-055 port** — a Qualcomm-native build for the higher-performance NPU hardware.
