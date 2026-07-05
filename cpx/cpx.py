"""CPX USB Read Example and chagne LEDs state based on USB read value.
This code will be run on the Circuit Playground Express (CPX) board. It will read data from the USB serial input and change the state of the onboard LED based on the received value.
Plan: it be via state machine"""

#Name needs to changed to code.py to run on the CPX board.

import time
from adafruit_circuitplayground import cp
import usb_cdc



serial = usb_cdc.data  # Use the data USB CDC interface for communication
buf = b""  # Buffer to hold incoming data


class State:
    """Enum-like class to represent different states. Not using the enum module to keep it simple for CircuitPython. And decrease RAM usage."""
    IDLE = "0"
    THUMBS_UP = "1"
    THUMBS_DOWN = "2"
    OPEN_PALM = "3"

def thumbs_up():
    """Display a thumbs up pattern on the CPX board."""
    cp.pixels[4] = (0, 255, 0)  # Green
    cp.pixels[5] = (0, 255, 0)  # Green
    cp.pixels[7] = (0, 255, 0)  # Green
    cp.pixels[8] = (0, 255, 0)  # Green
    cp.pixels[9] = (0, 255, 0)  # Green
    cp.pixels[0] = (0, 255, 0)  # Green
    cp.pixels[1] = (0, 255, 0)  # Green
    cp.pixels[2] = (0, 255, 0)  # Green


_td_phase = 0
_td_last = 0

def thumbs_down():
    """Non-blocking alternating checkerboard animation, one frame per call
    when ≥0.5s has elapsed since the last flip."""
    global _td_phase, _td_last
    now = time.monotonic()
    if now - _td_last < 0.5:
        return  # not time to flip yet
    _td_last = now
    on_even = _td_phase % 2 == 0
    for i in range(10):
        cp.pixels[i] = (255, 0, 0) if (i % 2 == 0) == on_even else (0, 0, 0)
    _td_phase += 1
  
    # while True:
    #     cp.pixels[0] = (255, 0, 0)  # Red
    #     cp.pixels[1] = (0, 0, 0)  
    #     cp.pixels[2] = (255, 0, 0)  # Red
    #     cp.pixels[3] = (0, 0, 0) 
    #     cp.pixels[4] = (0, 0, 0)  # Red
    #     cp.pixels[4] = (255, 0, 0)  # Red
    #     cp.pixels[5] = (0, 0, 0)
    #     cp.pixels[6] = (255, 0, 0)  # Red
    #     cp.pixels[7] = (0, 0, 0)
    #     cp.pixels[8] = (255, 0, 0)  # Red
    #     cp.pixels[9] = (0, 0, 0)
    #     time.sleep(0.5)
    #     cp.pixels[0] = (0, 0, 0)
    #     cp.pixels[1] = (255, 0, 0)  # Red
    #     cp.pixels[2] = (0, 0, 0)
    #     cp.pixels[3] = (255, 0, 0)  # Red
    #     cp.pixels[4] = (0, 0, 0)
    #     cp.pixels[5] = (255, 0, 0)  # Red
    #     cp.pixels[6] = (0, 0, 0)
    #     cp.pixels[7] = (255, 0, 0)  # Red
    #     cp.pixels[8] = (0, 0, 0)
    #     cp.pixels[9] = (255, 0, 0)  # Red  
    #     time.sleep(0.5)  

def open_palm():
    cp.pixels.fill((200,125,150))  # Animate the pixels with a blue pulse effect



def no_gesture():
    """No Gestures Detected"""
    cp.pixels.fill((0, 0, 0))  # Turn off all pixels

def apply_state(state):
    """Apply the given state to the CPX board."""

    if state == State.THUMBS_DOWN:
        thumbs_down()
    elif state == State.THUMBS_UP:
        thumbs_up()
    elif state == State.OPEN_PALM:
        open_palm()
    else:
        no_gesture()  # Default to no gesture if state is unrecognized


def read_usb():
    """Line read from USB serial."""
    global buf
    #If there are bytes waiting
    if serial.in_waiting:
        #Read the number of bytes waiting and add them to the buffer
        buf += serial.read(serial.in_waiting)
        #Check if we have a complete line (ending with newline character)
        if  b'\n' in buf:
            # line,seperator, buf = buf.partition(b'\n')  # Split of before seperator, seperator, and after seperator.
            # Buf us updated to contain the remaining data after the '\n'
            line, _, buf = buf.partition(b'\n')     
            line = line.decode().strip()
            return line
        else:
            return None
    else: 
        return None

"""Initialize the CPX board to the default state."""
cp.pixels.brightness = 0.01  # Set brightness to a reasonable level
curent_state = State.THUMBS_UP  # Start with the THUMBS_UP state
apply_state(curent_state)


"""Main loop to read commands from USB and change the state of the CPX board accordingly."""
while True:
    try:
        cmd = read_usb()
        if cmd is not None:
            if cmd in (State.IDLE, State.THUMBS_UP, State.THUMBS_DOWN, State.OPEN_PALM):
                curent_state = cmd
                apply_state(curent_state)
                serial.write(f"State: {curent_state}\n".encode())
                #print(f"State changed to: {curent_state}")
            else:
                serial.write(f"Unknown command: {cmd}\n".encode())
    except Exception as e:
        serial.write(f"Error: {str(e)}\n".encode())
    time.sleep(0.05)  # Small delay to avoid busy waiting
