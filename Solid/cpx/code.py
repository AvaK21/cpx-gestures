# code.py — Circuit Playground Express: react to gesture IDs from USB CDC data.
# Protocol: one ASCII integer per line, e.g. b"4\n". 0 = no gesture / idle.
import time

import usb_cdc
from adafruit_circuitplayground import cp

serial = usb_cdc.data
if serial is None:
    # boot.py missing or not yet applied — blink red forever as a diagnostic.
    while True:
        cp.pixels.fill((30, 0, 0))
        time.sleep(0.3)
        cp.pixels.fill(0)
        time.sleep(0.3)

serial.timeout = 0  # non-blocking reads

#Define colors for the gestures RGB
RED = (255, 0, 0)
LIGHT_BLUE = (0, 140, 255)
GREEN = (0, 255, 0)
PINK = (255, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (147, 0, 225)
NONE = (0, 0, 0)
GRAY = (127, 127, 127)


# gesture id -> (color, name)
REACTIONS = {
    0: (NONE, "idle"),
    1: (GREEN, "fist"),
    2: (LIGHT_BLUE, "palm"),
    3: (YELLOW, "point"),
    4: (GRAY, "thumb up"),
    5: (RED, "thumb down"),
    6: (PURPLE, "victory"),
    7: (PINK, "love"),
}

cp.pixels.brightness = .2
buf = b""
# Make sure the first gesture is sent
current = -1

while True:
    # Accumulate bytes until a newline; tolerate partial writes.
    data = serial.read(16)
    if data:
        buf += data
        while b"\n" in buf:
            line, _, buf = buf.partition(b"\n")
            try:
                gesture_id = int(line.strip())
            except ValueError:
                continue  # garbage on the line; skip it
            if gesture_id in REACTIONS and gesture_id != current:
                current = gesture_id
                color, name = REACTIONS[gesture_id]
                cp.pixels.fill(color)
                print("gesture:", name)  # visible on the REPL console port
                if gesture_id == 4:      # small flourish for thumbs-up
                    cp.play_tone(880, 0.1)
    time.sleep(0.01)