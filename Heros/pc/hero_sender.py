"""Detect hand gestures via MediaPipe and send gesture IDs to a CPX over USB CDC.

Protocol: ASCII digit + newline (e.g. b"4\n") sent ONLY when the debounced
gesture changes. The CPX side reads lines from usb_cdc.data.


Requires: #TODO: Add
Model:    gesture_recognizer.task
          https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task

"""

import sys
import time
import os


import cv2
import numpy as np
import serial
import serial.tools.list_ports
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from PIL import ImageFont, ImageDraw, Image


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_LOCATION = os.path.join(BASE_DIR, "font", "VERDANA.TTF")  # path to the font file
font = ImageFont.truetype(FONT_LOCATION, 30)  # load once, outside loop
TEXT_LOCATION = (10, 10)
MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "gesture_recognizer.task")  # path to the MediaPipe gesture recognizer model

# This is my COM port for the CPX data channel. Use Solid project to find your own.
# Once you find the correct port, you can hardcode it here for convenience.
CPX_PORT = "COM3"  
BAUD = 115200          # ignored by USB CDC, required by pyserial
MIN_SCORE = 0.50       # below this, treat as None
DEBOUNCE_FRAMES = 5    # consecutive frames required before accepting a gesture

GESTURE_IDS = {
    "None":         (0, (20,40,60,255),     "None"),  # (ID, RGB color, Hero name)
    "Closed_Fist":  (1, (0,255,0,255),      "HULK"),                    # Green
    "Open_Palm":    (2, (255,180,0,255),    "IRON MAN"),              # Gold
    "Pointing_Up":  (3, (255,255,0,255),    "THOR"),                    # Yellow
    "Thumb_Up":     (4, (100,149,237,255),  "CAPTAIN AMERICA"),   # Blue-ish
    "Thumb_Down":   (5, (255,0,255,255),    "THANOS"),                  # Magenta
    "Victory":      (6, (255,120,0,255),    "DOCTOR STRANGE"),          # Orange
    "ILoveYou":     (7, (255,0,0,255),      "SPIDERMAN")                # RED
}

class GestureDebouncer:
    """Sends a gesture only after it is present for N consecutive frames"""

    def __init__(self, frames_required = 5):
        self.frames_required = frames_required
        self._candidate = 0
        self._count = 0
        self.stable = 0
        self.current = 0

    def update(self, gesture_id: int) -> bool:
        """Checks a frame's classification. Returns True if `current` has changed"""
        if gesture_id == self._candidate: 
            self._count += 1
        else:
            self._candidate = gesture_id
            self._count = 1
        if self._count >= self.frames_required and self._candidate != self.current:
            self.current = self._candidate
            return True
        return False
        
def main() -> None: 
    ser = serial.Serial(CPX_PORT, BAUD, timeout = 0.1)

    #default settings 
    latest = {"id": 0, "color": (0,0,0,0), "name": None, "score": 0.0}
    
    def on_result(result, output_image, timestamp_ms):
        if result.gestures and result.gestures[0]:
            top = result.gestures[0][0] #first hand, top category
            if top.score >= MIN_SCORE:
                id,color,name = GESTURE_IDS.get(top.category_name, 0)
                latest["id"] = id
                latest["name"] = name
                latest["color"] = color
                latest["score"] = top.score
                return
        else:
            latest["id"], latest["color"], latest["name"], latest["score"] = 0,(0,0,0,0), None, 0.0



# MediaPipe runs on a background thread, so we can use the main thread to read from the webcam and send data to the CPX. 
# The callback will update the `latest` dictionary with the most recent gesture classification.
    options = vision.GestureRecognizerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=on_result,
        num_hands=1,
    )

    debouncer = GestureDebouncer(DEBOUNCE_FRAMES)
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hero Sender", cv2.WINDOW_NORMAL)
    if not cap.isOpened():
        sys.exit("ERROR: Can't open webcam.")

    print("Press 'q' to quit in preview window.")

#maube where to use the timestamp_ms
    last_ts = 0  # last timestamp submitted to MediaPipe

    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # mirror view

# Cv2 uses BGR color order, but MediaPipe expects RGB. Convert the frame to RGB before sending it to MediaPipe.
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB, 
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )
            ts = int(time.monotonic() * 1000)
            if ts <= last_ts:
                ts = last_ts + 1
            last_ts = ts
            #submit the frame to mediapipe asynchronously, so that the callback can be called on a background thread
            recognizer.recognize_async(mp_image, timestamp_ms=ts)


            if debouncer.update(latest["id"]):
                if latest["id"] is not None:
                    msg = f"{debouncer.current}\n".encode()
                    ser.write(msg)
                    
                    

                    print(f"Sent: {debouncer.current}")

            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
            overlay = Image.new("RGBA", img_pil.size, (0,0,0,0))
            draw_overlay = ImageDraw.Draw(overlay)
            
            name = latest['name'] if latest['name'] is not None else "None"
            text = f"{name}: {(latest['score'] *100):.2f}%"
            bbox = draw_overlay.textbbox(TEXT_LOCATION, text = text, font = font)
            padding = 3
            draw_overlay.rectangle(
                (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding),
                fill=(0,0,0,30)
            )
            draw_overlay.text(TEXT_LOCATION, text=text, font=font, fill= latest['color'])
            img_pil = Image.alpha_composite(img_pil,overlay).convert("RGB")
            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            cv2.imshow("Hero Sender", frame)
            #hex 0xFF masks the lower 8 bits of the return value, which is necessary because cv2.waitKey() returns a 32-bit integer, but we only care about the lower 8 bits (the ASCII value of the key pressed).
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    ser.write(b"0\n")  # send None on exit
    ser.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
            
