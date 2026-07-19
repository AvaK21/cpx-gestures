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

INTERVAL = 0.20
IRON_MAN_STEP = 30

ANIMATED = {2,3, 7}  # set of gesture IDs that should be animated (spiderman)

iron_man_brightness = 0
iron_man_direction = 1
spiderman_state = False

THOR_LEFT_START = 9
THOR_RIGHT_START = 0
thor_left = THOR_LEFT_START
thor_right = THOR_RIGHT_START
thor_direction = 1  # 1 for expanding, -1 for contracting

def hulk():
    cp.pixels.fill(GREEN)


def iron_man():
    global iron_man_brightness, iron_man_direction
    iron_man_brightness += iron_man_direction * IRON_MAN_STEP
    if iron_man_brightness >= 255:
        iron_man_brightness = 255
        iron_man_direction = -1
    elif iron_man_brightness <= 0:
        iron_man_brightness = 0
        iron_man_direction = 1
    cp.pixels.fill((0,0,iron_man_brightness))


def thor():
    global thor_left, thor_right, thor_direction
    if thor_direction == 1:  # Expanding
        cp.pixels[thor_left] = YELLOW
        cp.pixels[thor_right] = YELLOW
        thor_left -= 1
        thor_right += 1
        if thor_right >= 5 or thor_left < 5:
            thor_direction = -1  # Switch to contracting
            thor_left = 5
            thor_right = 4
    else:  # Contracting
        cp.pixels[thor_left] = NONE
        cp.pixels[thor_right] = NONE
        thor_left += 1
        thor_right -= 1
        if thor_left > THOR_LEFT_START or thor_right < THOR_RIGHT_START:
            thor_direction = 1  # Switch to expanding
            thor_left = THOR_LEFT_START
            thor_right = THOR_RIGHT_START




def captain_america():
    cp.pixels.fill(BLUEISH)


def thanos():
    cp.pixels.fill(MAGENTA)


def doctor_strange():
    cp.pixels.fill(ORANGE)


def spiderman():
    global spiderman_state
    if spiderman_state:
        cp.pixels[0::2] = [RED] * 5
        cp.pixels[1::2] = [BLUE] * 5
    else:
        cp.pixels[0::2] = [BLUE] * 5
        cp.pixels[1::2] = [RED] * 5
    spiderman_state = not spiderman_state



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
gesture_id = 0  # Initialize gesture_id to a default value
last = time.monotonic()  # Initialize last to the current time

while True:
    if serial.in_waiting > 0:
    # Accumulate bytes until a newline; tolerate partial writes.
        data = serial.read(serial.in_waiting)
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
                    cp.pixels.brightness = 0.05
                    ACTIONS[gesture_id]()
                    print("Index:", gesture_id)
    now = time.monotonic()
    # print("Current:", current, "Last:", last, "Now:", now)
    if current in ANIMATED and now - last >= INTERVAL:
                print(float(now - last))
                last = now
                ACTIONS[current]()

    time.sleep(.001)
