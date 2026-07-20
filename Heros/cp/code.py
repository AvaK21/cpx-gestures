import time
import usb_cdc
from random import randint
from adafruit_circuitplayground import cp
import gc



serial = usb_cdc.data
if serial is None:

    while True:
        cp.pixels.fill((30, 0, 0))
        time.sleep(0.3)
        cp.pixels.fill(0)
        time.sleep(0.3)


GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
BLUEISH = (0,100,255)
MAGENTA = (255,0,255)
ORANGE = (255,120,0)
RED = (255,0,0)
NONE = (0,0,0)
WHITE = (255,255,255)

INTERVAL = 0.20
IRON_MAN_STEP = 30



iron_man_brightness = 0
iron_man_direction = 1
spiderman_state = False

THOR_LEFT_START = 9
THOR_RIGHT_START = 0
thor_left = THOR_LEFT_START
thor_right = THOR_RIGHT_START
thor_direction = 1  

thanos_index = 0
cap_index = 0

hulk_index = 0


def hulk():
    global hulk_index
    if hulk_index == 0:
        cp.pixels.fill(NONE)

    cp.pixels[hulk_index] = GREEN
    hulk_index = (hulk_index + 1) % 10

    

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
    if thor_direction == 1: 
        cp.pixels[thor_left] = YELLOW
        cp.pixels[thor_right] = YELLOW
        thor_left -= 1
        thor_right += 1
        if thor_right >= 5 or thor_left < 5:
            thor_direction = -1  
            thor_left = 5
            thor_right = 4
    else:  
        cp.pixels[thor_left] = NONE
        cp.pixels[thor_right] = NONE
        thor_left += 1
        thor_right -= 1
        if thor_left > THOR_LEFT_START or thor_right < THOR_RIGHT_START:
            thor_direction = 1  
            thor_left = THOR_LEFT_START
            thor_right = THOR_RIGHT_START




def captain_america():
    global cap_index
    cp.pixels.fill(BLUEISH)       
    cp.pixels[cap_index] = WHITE   
    cap_index = (cap_index + 1) % 10


def thanos():
    global thanos_index
    if(thanos_index == 0):
        cp.pixels.fill(MAGENTA)
    elif( 1 <= thanos_index <= 5):
        pass 
    elif(thanos_index == 6):
        for i in range(10):
            cp.pixels[i] = MAGENTA if randint(0,1) == 0 else NONE
    elif(7 <= thanos_index <= 11):
        pass  
    thanos_index += 1
    if thanos_index > 11:
        thanos_index = 0



def doctor_strange():
    cp.pixels.brightness = 0.2
    for i in range(10):
        roll = randint(0,2)
        hue = randint(110,255)
        if roll == 0:      
            cp.pixels[i] = (hue, 120, 0)  
        elif roll == 1:
            cp.pixels[i] =  (hue, 0, 0)  
        else:
            cp.pixels[i] = (0, 0, 0)  

        


def spiderman():
    global spiderman_state
    a,b = (RED,BLUE) if spiderman_state else (BLUE,RED)
    for i in range(10):
        cp.pixels[i] = a if i%2 == 0 else b
    spiderman_state = not spiderman_state

def clear_hulk():
    global hulk_index
    hulk_index = 0

def clear_iron_man():
    global iron_man_brightness, iron_man_direction
    cp.pixels.brightness = 0.05
    iron_man_brightness = 0
    iron_man_direction = 1

def clear_thor():
    global thor_left, thor_right, thor_direction
    thor_left = THOR_LEFT_START
    thor_right = THOR_RIGHT_START
    thor_direction = 1


def clear_spiderman():
    global spiderman_state
    spiderman_state = False

def clear_thanos():
    global thanos_index
    thanos_index = 0

def clear_captain_america():
    global cap_index
    cap_index = 0

def clear_doctor_strange():
    cp.pixels.brightness = 0.05

def idle():
    cp.pixels.fill(NONE)

ACTIONS = {
    0:  (idle,            idle),
    1:  (hulk,            clear_hulk),
    2:  (iron_man,        clear_iron_man),
    3:  (thor,            clear_thor),
    4:  (captain_america, clear_captain_america),
    5:  (thanos,          clear_thanos),
    6:  (doctor_strange,  clear_doctor_strange),
    7:  (spiderman,       clear_spiderman),
    -1: (idle,            idle),
}



serial.timeout = 0  

cp.pixels.brightness = 0.05
buf = b""
current = -1  
gesture_id = 0  
last = time.monotonic()  

print(f"RAM free: {gc.mem_free()} bytes") 

while True:

    if serial.in_waiting > 0:

        data = serial.read(serial.in_waiting)
        if data:
            buf += data
            while b"\n" in buf:
                line, _, buf = buf.partition(b"\n")
                try:
                    gesture_id = int(line.strip())
                except ValueError:
                    continue 
                if  0 <= gesture_id <= 7 and gesture_id != current:
                    gc.collect()
                    ACTIONS[current][1]() 
                    current = gesture_id
                    ACTIONS[gesture_id][0]()
    now = time.monotonic()

    if current not in (0,-1) and now - last >= INTERVAL:
        last = now
        ACTIONS[current][0]()

    time.sleep(.001)