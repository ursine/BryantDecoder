#!/usr/bin/env python3

import os
import termios
import time
from typing import List

from decode import find_frames

PORT = "/dev/ttyUSB0"
BAUD = 38400
BAUD_CONST = termios.B38400

try:
    fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY)
except OSError as e:
    raise RuntimeError(f"Could not open port {PORT}: {e}")

new_attrs = termios.tcgetattr(fd)

# Set the input and output baud rates.
new_attrs[4] = BAUD_CONST  # Index 4 is the input speed.
new_attrs[5] = BAUD_CONST  # Index 5 is the output speed.

# Configure the control modes (cflag):
# - Set 8 bits per byte (CS8)
# - Disable parity (clear PARENB)
# - Set one stop bit (clear CSTOPB)
# - Ignore modem control lines (CLOCAL)
# - Enable receiver (CREAD)
new_attrs[2] &= ~termios.PARENB   # No parity.
new_attrs[2] &= ~termios.CSTOPB   # 1 stop bit.
new_attrs[2] &= ~termios.CSIZE    # Clear current data size setting.
new_attrs[2] |= termios.CS8       # 8 data bits.
new_attrs[2] |= (termios.CLOCAL | termios.CREAD)

# Configure local modes (lflag) to disable canonical mode, echo, signals, etc.
new_attrs[3] = 0

# Disable any input (iflag) and output (oflag) processing.
new_attrs[0] = 0  # iflag
new_attrs[1] = 0  # oflag

# Control characters: VMIN and VTIME control read behavior.
# VMIN = 1: read() will block until at least 1 byte is received.
# VTIME = 0: no timeout.
new_attrs[6][termios.VMIN] = 1
new_attrs[6][termios.VTIME] = 0

# Apply the settings immediately.
termios.tcsetattr(fd, termios.TCSANOW, new_attrs)

inMessage = False
inQueue: List[int] = []
found = True

message = []

print("Starting to read from the serial port (press Ctrl+C to exit)...")
try:
    while True:
        # os.read blocks until at least 1 byte is available because VMIN is set to 1.
        data = os.read(fd, 1024)  # Read up to 1024 bytes.

        inQueue.extend([int(x) for x in data])

        found, frame, inQueue = find_frames(inQueue)

        if found:
            print(found, frame)
            fdata = frame.data
            if len(fdata)>3 and fdata[0]==0 and fdata[1]==0x01 and fdata[2]==0x04:
                print("INFO FRAME!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Exiting read loop.")

