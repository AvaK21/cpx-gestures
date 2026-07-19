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

#DEFINE Colors
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
BLUEISH = (100,149,237)
MAGENTA = (255,0,255)
ORANGE = (255,120,0)
RED = (255,0,0)
NONE = (0,0,0)

hulk = lambda: cp.pixels.fill(GREEN)

iron_man = lambda: cp.pixels.fill(BLUE)

thor = lambda: cp.pixels.fill(YELLOW)

captain_america = lambda: cp.pixels.fill(BLUEISH)

thanos = lambda: cp.pixels.fill(MAGENTA)

doctor_strange = lambda: cp.pixels.fill(ORANGE)

spiderman = lambda: cp.pixels.fill(RED)



#CPX doesn't have a built-in way to do a switch statement, so we use a if/el
ACTIONS = {
    0: lambda: cp.pixels.fill(NONE),
    1: hulk,
    2: iron_man,
    3: thor,
    4: captain_america,
    5: thanos,
    6: doctor_strange,
    7: spiderman
}




serial.timeout = 0  # non-blocking reads

cp.pixels.brightness = 0.05
buf = b""
current = -1  # Make sure the first gesture is sent

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
                continue #garbage on the line, skip it
            if  0 <= gesture_id <= 7 and gesture_id != current:
                current = gesture_id
                ACTIONS[gesture_id]()
                print("Index:", gesture_id)
    time.sleep(.01)
