FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libgl1 libglib2.0-0 libusb-1.0-0 \
    libxcb1 libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
    libxcb-render-util0 libxcb-shape0 libxcb-shm0 libxcb-xfixes0 \
    libx11-xcb1 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY app/main.py .

CMD ["python3", "main.py"]
