#!/usr/bin/env python3

import os
import termios
import time

PORT = "/dev/ttyUSB0"
BAUD = 38400
BAUD_CONST = termios.B38400


try:
    fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY)
except OSError as e:
    raise RuntimeError(f"Could not open port {port}: {e}")

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


def crc16(data: bytes, poly: int = 0x8005, init: int = 0) -> int:
    """
    Compute a CRC16 using the polynomial 0x8005 in non-reflected mode.

    Args:
        data (bytes): Input data to compute the CRC on.
        poly (int): Polynomial to use (default 0x8005).
        init (int): Initial CRC value (default 0).

    Returns:
        int: The computed CRC16 value.
    """
    crc = init
    for byte in data:
        # Bring the byte into the high-order 8 bits of the 16-bit CRC.
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:  # If the uppermost bit is set...
                crc = ((crc << 1) ^ poly) & 0xFFFF  # Shift left and XOR with poly.
            else:
                crc = (crc << 1) & 0xFFFF  # Otherwise, just shift left.
    return crc


inMessage = False
inQueue = []

message = []

print("Starting to read from the serial port (press Ctrl+C to exit)...")
try:
    while True:
        # os.read blocks until at least 1 byte is available because VMIN is set to 1.
        data = os.read(fd, 1024)  # Read up to 1024 bytes.

        inQueue.extend(data)

        #if len(inQueue) < 10:
        #    continue

#        val = 0
#        count = 0
#        while val == 0:
#            val = inQueue.pop(0)
#            count+=1

#        print(f"Skipped {count} zeroes") 
            
#        destAddr = val
#        destBus = inQueue.pop(0)
#        srcAddr = inQueue.pop(0)
#        srcBus = inQueue.pop(0)
#        length = inQueue.pop(0)
#        pid = inQueue.pop(0)
#        ext = inQueue.pop(0)
#        function = inQueue.pop(0)
#        data = inQueue[:length]
#        checksum = inQueue.pop(0) * 256 + inQueue.pop(1)

#        checksumCheck = [destAddr, destBus, srcAddr, srcBus, length, pid, ext, function]
#        checksumCheck.extend(data)

#        crc = crc16(bytes(checksumCheck))
          
 #       print(f"Data: {destAddr} {destBus} {srcAddr} {srcBus} {length} {pid} {ext} {function} {checksum}=={crc}")

        
        #if data:
        #    # Print the raw bytes and also a hex representation.
        #    print(f"Received {len(message)} bytes: {data}")
        print("Hex:", bytes(data).hex())
        #    # Optionally, sleep briefly to avoid a busy loop.
        #    time.sleep(0.01)
except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Exiting read loop.")

