import os
import cv2
import time
import serial
import serial.tools.list_ports
from hand_analyzer import HandAnalyzer

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_PATH,"..\..","Models", "hand_landmarker.task")
CPX_PORT = "COM3"  # Change this to your CPX data channel port, or None to auto-detect.
BAUD = 115200  # ignored by USB CDC, required by pyserial
DEBOUNCE_FRAMES = 5  # consecutive frames required before accepting a gesture

# TODO add try exeception block on open camera and the options line - when would expect errors - other sources, inputs, 
# TODO add input for if the CPX_PORT is empty for user to type answer and have try except 


class Debouncer:
    """Accepts a number only after it is held after N consecutive frames."""

    def __init__(self, frames_required:int = 5):
        self.frames_required = frames_required
        self._candidate = None
        self._count = 0
        self.current = None

    def update(self, extended: int) -> bool:
        """Feed extended results. Returns True if current has changed"""
        if extended == self._candidate:
            self._count +=1
        else:
            self._candidate = extended
            self._count = 1
        if self._count >= self.frames_required and self._candidate != self.current:
            self.current = self._candidate
            return True
        return False












def main() -> None:
    try:
        ser = serial.Serial(port=CPX_PORT, baudrate=BAUD, timeout=0.1) if CPX_PORT else None
    except serial.SerialException as e:
        print(f"Error opening serial port {CPX_PORT}: {e}")
        ser = None



    debouncer = Debouncer(DEBOUNCE_FRAMES)

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hand Tracking", cv2.WINDOW_NORMAL)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    print("Press q on the cv2 window to exit")
    last_ts = 0
    p_time = time.time()


    num_extended = 0

    analyzer = HandAnalyzer(MODEL_PATH)

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            continue 
        frame = cv2.flip(frame, 1)

        # If the timestamp is not greater than the previous timestamp, increment it by 1 to ensure that the timestamps are monotonically increasing.
        # Otherwise the program will almost always crash immediately:
        ts = int(time.time() * 1000)
        if ts <= last_ts:
            ts = last_ts + 1
        last_ts = ts

        analyzer.process_frame(frame, ts)

        results  = analyzer.analyze_results(frame)
        num_extended = results[1] if results is not None and results[1] is not None else 0

        updated = debouncer.update(num_extended)
        if updated:
            if num_extended is not None and ser is not None:
                msg = f"{num_extended}\n".encode()
                try:
                    ser.write(msg)
                except serial.SerialException as e:
                    print(f"Error writing to serial port: {e}")
            #print(f"Extended: {num_extended} fingers detected.")

        c_time = time.time()
        fps = 1 / (c_time - p_time ) if p_time != 0 else 0
        p_time = c_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Hand Tracking", frame)

        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    del debouncer
    analyzer.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()