# i.MX95 Board Setup

This guide covers installing and running the eIQ GenAI Flow 2.0 demo on the i.MX95 board.

---

# Overview

The i.MX95 board is responsible for:

- Running the LLM
- Running Retrieval-Augmented Generation (RAG)
- Speech Recognition (ASR)
- Text-to-Speech (TTS)
- Answering user questions

The board does **not** generate the RAG database.

---

# Prerequisites

- AOM-5521 / i.MX95 board running Yocto 5.0
- HDMI monitor
- USB keyboard
- USB flash drive
- Ubuntu Host PC
- Internet connection
- Generated `rag_database.pkl` from the Host PC
---

# Accessing the AOM-5521 / i.MX95 Board serial console

- There are 2 COM ports present on the main board
- Connect the one without the red wire to an external PC (a COM to USB adapter works)
- Use ```lsusb``` to verify the the COM adapter is visible to the PC
- Use `screen` to access the board's terminal
- The board exposes a serial console through one of its USB-UART ports. A serial terminal such as `screen` or `picocom` can be used to interact with the board from the Host PC.
- Run this command to connect to the board, you may have to change the USB number depending on where your USB is plugged in

```
sudo screen /dev/ttyUSB0 115200
```

`picocom` also works

```
sudo picocom -b 115200 /dev/ttyUSB0
```

---

# Install Git

Skip if Git is already installed.

```bash
cd ~

wget https://www.kernel.org/pub/software/scm/git/git-2.9.5.tar.gz

tar -zxf git-2.9.5.tar.gz

cd git-2.9.5

make prefix=/usr/local all

sudo make prefix=/usr/local install

cd ~

rm -r git-2.9.5

rm git-2.9.5.tar.gz
```

---

# Install Git LFS

```bash
cd ~

wget https://github.com/git-lfs/git-lfs/releases/download/v3.7.1/git-lfs-linux-arm64-v3.7.1.tar.gz

tar -xf git-lfs-linux-arm64-v3.7.1.tar.gz

cd git-lfs-3.7.1

chmod +x install.sh

./install.sh

cd ~

rm -r git-lfs-3.7.1

rm git-lfs-linux-arm64-v3.7.1.tar.gz
```

---

# Clone the Project

```bash
git clone --single-branch -b release/v2.0 \
https://github.com/nxp-appcodehub/dm-eiq-genai-flow-demonstrator
```

---

# Download LFS Files

Git LFS is used to download the large AI model files that are not stored directly in the Git repository.

```bash
cd dm-eiq-genai-flow-demonstrator

git lfs pull
```

---

# Install

Run the installation script to download the required Python packages, AI models, and runtime dependencies.

```bash
./install.sh
```

---

# Copy the RAG Database

The Host PC generates `rag_database.pkl`, which contains the document embeddings and metadata used during Retrieval-Augmented Generation (RAG).

Copy this file onto a USB flash drive and insert it into the AOM-5521.

```
rag_database.pkl
```

into

```
rag/src/data/
```

## Copy the RAG Database from a USB Drive

After generating `rag_database.pkl` on the host PC, copy the file to a USB flash drive and insert it into the i.MX95 board.

### 1. Identify the USB Device

Run:

```bash
lsblk
```

This lists all block storage devices connected to the system.

Example output:

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    1 58.6G  0 disk
└─sda1   8:1    1 58.6G  0 part
```

In this example, the USB drive is detected as `/dev/sda1`.

### 2. Mount the USB Drive

Mount the USB drive so its files can be accessed by the operating system.

```bash
mount /dev/sda1 /mnt/usb
```

This makes the contents of the USB drive available under:

```
/mnt/usb
```

### 3. Copy the RAG Database

Copy the generated RAG database into the application's data directory.

```bash
cp /mnt/usb/rag_database.pkl \
~/dm-eiq-genai-flow-demonstrator/rag/src/data/
```

After copying, the application will use this database for Retrieval-Augmented Generation (RAG).

### Verification

Confirm that the file was copied successfully:

```bash
ls ~/dm-eiq-genai-flow-demonstrator/rag/src/data/
```

You should see:

```
rag_database.pkl
```

---

# Launch with RAG Enabled

```bash
python3 eiq_genai_flow.py -r
```

The `-r` flag enables Retrieval-Augmented Generation.

---

## Using the Assistant

After the application has finished loading, enter a question at the prompt.

If relevant information exists in the RAG database, the system retrieves the appropriate document sections and uses them as context for the LLM before generating a response.
---

# USB Audio Devices

To view available audio devices:

```bash
python3 eiq_genai_flow.py -h
```

Example device

```
plughw:CARD-Seri
```

> **Note**
>
> During testing, USB speaker playback only functioned reliably when the LLM was unable to answer a question. The speech output also played back significantly faster than expected.
>
> Microphone input could not be successfully configured during testing, so voice interaction was not validated as part of this setup.
---

# Runtime Pipeline

```
Microphone

↓

Speech Recognition

↓

Question

↓

RAG Retrieval

↓

LLM

↓

Generated Answer

↓

Text-to-Speech

↓

Speaker
```

---

# Notes

- The board only consumes the generated database.
- If PDFs change, regenerate `rag_database.pkl` on the host PC and copy the new file to the board.
- Always launch with `-r` when using custom documents.


# Troubleshooting

## Cannot connect with `screen`

- Verify the USB-UART cable is connected to the correct COM port on the carrier board.
- Check the detected serial device:

```bash
ls /dev/ttyUSB*
```

- Connect using:

```bash
sudo screen /dev/ttyUSB0 115200
```

or

```bash
sudo picocom -b 115200 /dev/ttyUSB0
```

## Board enters the SM Debug Monitor

If the board displays:

```
*** SM Debug Monitor ***
>$
```

verify that the serial cable is connected to the correct UART port on the carrier board. Connecting to the debug UART instead of the Linux console UART may result in this prompt instead of the Linux login shell.

## USB drive not detected

Verify the device appears using:

```bash
lsblk
```

The USB drive should typically appear as `/dev/sda1`.
