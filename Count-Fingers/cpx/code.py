import time 
import usb_cdc
from random import randint
import gc
from adafruit_circuitplayground import cp

DEFAULT_BRIGHTNESS  = 0.05

try:
    
    if usb_cdc.data is None:
        raise RuntimeError("No serial connection available or no boot.py enable data.")
    serial = usb_cdc.data
    serial.timeout = 0
except RuntimeError as e:
    print(e)
    while True:
        cp.pixels.fill((200, 0, 0))
        time.sleep(0.5)
        cp.pixels.fill((0, 0, 0))
        time.sleep(0.5)


cp.pixels.brightness = DEFAULT_BRIGHTNESS
buf = b""
current = -1
extended = -1
color = (200, 0, 200)
print(f"RAM free: {gc.mem_free()} bytes")

while True:
    if serial.in_waiting > 0:
        data = serial.read(serial.in_waiting)
        if data:
            buf += data
            while b"\n" in buf:
                line, _, buf = buf.partition(b"\n")
                try:
                    extended = int(line.strip())
                except ValueError as e:
                    print(f"Invalid data received: {line.strip()} error: {e}")
                    continue
                if 0 <= extended <=10 and extended != current:
                    if extended < current:
                        cp.pixels.fill((0, 0, 0))
                    current = extended
                    if extended == 10:
                        color = (randint(0, 255), randint(0, 255), randint(0, 255))
                    for i in range(current):
                        cp.pixels[i] = color
                time.sleep(0.001)

