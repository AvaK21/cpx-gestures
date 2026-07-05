"""Detect hand gestures via MediaPipe and send gesture IDs to a CPX over USB CDC.

Protocol: ASCII digit + newline (e.g. b"4\n") sent ONLY when the debounced
gesture changes. The CPX side reads lines from usb_cdc.data.

Requires: mediapipe, opencv-python (pulled in by mediapipe), pyserial
Model:    gesture_recognizer.task
          https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task
"""

import sys
import time

import cv2
import serial
import serial.tools.list_ports
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_PATH = "gesture_recognizer.task"
BAUD = 115200          # ignored by USB CDC, required by pyserial
MIN_SCORE = 0.60       # below this, treat as None
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


# def find_cpx_data_port() -> str:
#     """Find the CPX *data* CDC port (not the REPL console).

#     The CPX (VID 0x239A) exposes two CDC interfaces when boot.py enables
#     the data channel. CircuitPython enumerates the console first, data
#     second, so we take the highest-numbered matching port.
#     """
#     cpx_ports = sorted(
#         p.device for p in serial.tools.list_ports.comports() if p.vid == 0x239A
#     )
#     if not cpx_ports:
#         sys.exit("No CPX found. Is it plugged in?")
#     if len(cpx_ports) == 1:
#         sys.exit(
#             f"Only one CPX port found ({cpx_ports[0]}) — that's the REPL console.\n"
#             "The data CDC port is missing: copy boot.py to CIRCUITPY and "
#             "power-cycle the board (boot.py only runs on hard reset)."
#         )
#     print(f"CPX ports: {cpx_ports} -> using data port {cpx_ports[-1]}")
#     return cpx_ports[-1]


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
    port = "COM3"
    ser = serial.Serial(port, BAUD, timeout=0.1)

    # Latest result from the async callback, consumed by the main loop.
    latest = {"id": 0, "name": "None", "score": 0.0}

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
    if not cap.isOpened():
        sys.exit("Cannot open webcam.")

    print("Running. Press q in the preview window to quit.")
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
            recognizer.recognize_async(mp_image, int(time.monotonic() * 1000))

            if debouncer.update(latest["id"]):
                msg = f"{debouncer.stable}\n".encode()
                ser.write(msg)
                print(f"sent {msg!r}  ({latest['name']} @ {latest['score']:.2f})")

            cv2.putText(
                frame,
                f"{latest['name']} ({latest['score']:.2f})  stable={debouncer.stable}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
            )
            cv2.imshow("gesture-sender", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    ser.write(b"0\n")  # reset CPX to idle on exit
    ser.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()