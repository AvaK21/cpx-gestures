"""Detect hand gestures via MediaPipe and send gesture IDs to a CPX over USB CDC.

Protocol: ASCII digit + newline (e.g. b"4\n") sent ONLY when the debounced
gesture changes. The CPX side reads lines from usb_cdc.data.

Requires: mediapipe, opencv-python (pulled in by mediapipe), pyserial
Model:    gesture_recognizer.task
          https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task
"""

import sys
import time
from PIL import ImageFont, ImageDraw, Image
import os
import cv2
import numpy as np
import serial
import serial.tools.list_ports
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
font_location = os.path.join(BASE_DIR, "font", "VERDANA.TTF")  # path to the font file
font = ImageFont.truetype(font_location, 30)  # load once, outside loop
TEXT_LOCATION = (10,10)
MODEL_PATH =  os.path.join(BASE_DIR, "..", "..", "gesture_recognizer.task")  # path to the MediaPipe gesture recognizer model


# Serial port for the CPX *data* CDC channel (NOT the REPL console).
# Set to your port, or None to auto-detect.
#   Finding yours: with boot.py installed and the board power-cycled, the CPX
#   shows TWO COM ports (Windows: Device Manager > Ports; or
#   `python -m serial.tools.list_ports -v`). The console enumerates first,
#   data second — you want the second/higher one.
#   NOTE: Windows may reassign COM numbers if you use a different USB port
#   or plug in other serial devices. If gestures send but the CPX is dark,
#   re-check this first (or set to None).

#This is my COM port for the CPX data channel. Change it to None to auto-detect.
CPX_PORT = "COM3"
BAUD = 115200          # ignored by USB CDC, required by pyserial
MIN_SCORE = 0.50       # below this, treat as None
DEBOUNCE_FRAMES = 5    # consecutive frames required before accepting a gesture

GESTURE_IDS = {
    "None": 0,
    "Closed_Fist": 1,
    "Open_Palm": 2,
    "Pointing_Up": 3,
    "Thumb_Up": 4,
    "Thumb_Down": 5,
    "Victory": 6,
    "ILoveYou": 7,
}


def find_cpx_data_port() -> str:
    """Find the CPX *data* CDC port (not the REPL console).

    The CPX (VID 0x239A) exposes two CDC interfaces when boot.py enables
    the data channel. CircuitPython enumerates the console first, data
    second, so we take the highest-numbered matching port.
    """
    cpx_ports = sorted(
        p.device for p in serial.tools.list_ports.comports() if p.vid == 0x239A
    )
    if not cpx_ports:
        sys.exit("No CPX found. Is it plugged in?")
    if len(cpx_ports) == 1:
        sys.exit(
            f"Only one CPX port found ({cpx_ports[0]}) — that's the REPL console.\n"
            "The data CDC port is missing: copy boot.py to CIRCUITPY and "
            "power-cycle the board (boot.py only runs on hard reset)."
        )
    print(f"CPX ports: {cpx_ports} -> using data port {cpx_ports[-1]}")
    return cpx_ports[-1]


def resolve_port() -> str:
    """Use CPX_PORT if set, but verify it's actually a CPX data port."""
    if CPX_PORT is None:
        return find_cpx_data_port()
    cpx_ports = sorted(
        p.device for p in serial.tools.list_ports.comports() if p.vid == 0x239A
    )
    if CPX_PORT not in cpx_ports:
        sys.exit(
            f"CPX_PORT is {CPX_PORT!r}, but CPX ports found are {cpx_ports or 'none'}.\n"
            f"Windows may have reassigned the port — update CPX_PORT or set it "
            f"to None for auto-detect."
        )
    if cpx_ports and CPX_PORT == cpx_ports[0] and len(cpx_ports) > 1:
        print(
            f"WARNING: {CPX_PORT} is the FIRST CPX port (likely the REPL "
            f"console). The data port is usually {cpx_ports[-1]}."
        )
    return CPX_PORT


class GestureDebouncer:
    """Accept a gesture only after it holds for N consecutive frames."""

    def __init__(self, frames_required: int):
        self.frames_required = frames_required
        self._candidate = 0
        self._count = 0
        self.stable = 0  # currently accepted gesture ID

    def update(self, gesture_id: int) -> bool:
        """Feed one frame's classification. Returns True if `stable` changed."""
        if gesture_id == self._candidate:
            self._count += 1
        else:
            self._candidate = gesture_id
            self._count = 1
        if self._count >= self.frames_required and self._candidate != self.stable:
            self.stable = self._candidate
            return True
        return False


def main() -> None:
    port = resolve_port()
    ser = serial.Serial(port, BAUD, timeout=0.1)

    # Latest result from the async callback, consumed by the main loop.
    latest = {"id": 0, "name": "None", "score": 0.0}
# The function below is called by MediaPipe on a background thread when a new result is available. It updates the `latest` dict with the top gesture ID, name, and score. 
# The main loop reads `latest` and sends it to the CPX if it has stabilized.
    def on_result(result, output_image, timestamp_ms):
        if result.gestures and result.gestures[0]:
            top = result.gestures[0][0]  # first hand, top category
            if top.score >= MIN_SCORE:
                latest["id"] = GESTURE_IDS.get(top.category_name, 0)
                latest["name"] = top.category_name
                latest["score"] = top.score
                return
        latest["id"], latest["name"], latest["score"] = 0, "None", 0.0

    options = vision.GestureRecognizerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=on_result,
        num_hands=1,
    )

    debouncer = GestureDebouncer(DEBOUNCE_FRAMES)
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("gesture-sender", cv2.WINDOW_NORMAL)
    if not cap.isOpened():
        sys.exit("Cannot open webcam.")

    print("Running. Press q in the preview window to quit.")
    last_ts = 0  # last timestamp submitted to MediaPipe
    # with statement ensures the recognizer is cleaned up properly on exit. 
    # The main loop reads frames from the webcam, 
    # flips them for a mirror view, converts to RGB, and sends to MediaPipe. 
    # The async callback updates `latest`, which is debounced and sent to the CPX over serial when stable. 
    # The preview window shows the current gesture and score.
    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # mirror for natural interaction

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            )
            # MediaPipe requires STRICTLY increasing timestamps. int-ms
            # truncation can produce duplicates within the same millisecond,
            # so force forward progress on collision.
            ts = int(time.monotonic() * 1000)
            if ts <= last_ts:
                ts = last_ts + 1
            last_ts = ts
            recognizer.recognize_async(mp_image, ts)

            if debouncer.update(latest["id"]):
                msg = f"{debouncer.stable}\n".encode()
                ser.write(msg)
                print(f"sent {msg!r}  ({latest['name']} @ {latest['score']:.2f})")

            #Added a transpartent to have transparent background for the text overlay. 
            # This is done by creating a new RGBA image for the overlay, drawing the text and a semi-transparent rectangle behind it, 
            # and then compositing it with the original frame. The final frame is then converted back to RGB for OpenCV display.
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
            overlay = Image.new("RGBA", img_pil.size,(0,0,0,0))
            draw_overlay = ImageDraw.Draw(overlay)
            text = f"{latest['name']} ({(latest['score'] * 100):.0f}%)"
            bbox = draw_overlay.textbbox(TEXT_LOCATION, text=text, font=font)
            padding = 3
            draw_overlay.rectangle(
                (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding),
                fill=(0,0,0,30) #black, semi-transparent
            )
            draw_overlay.text(TEXT_LOCATION, text = text, font = font, fill=(0,20,100,255))

            img_pil = Image.alpha_composite(img_pil,overlay).convert("RGB")
            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            cv2.imshow("gesture-sender", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    ser.write(b"0\n")  # reset CPX to idle on exit
    ser.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()