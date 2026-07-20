# CPX Gesture Controller

Detects hand gestures via webcam using MediaPipe's GestureRecognizer task and
sends the result over USB serial to an Adafruit Circuit Playground Express
(CPX), which reacts by changing its NeoPixel color.

```
[Webcam] → MediaPipe GestureRecognizer (LIVE_STREAM) → Debounce → USB CDC (data)
                                                                        ↓
                                                    [CPX] boot.py enables data CDC
                                                          code.py reads line, reacts
```
## Gesture → ID mapping

| ID | Gesture | ID | Gesture |
|----|---------|----|---------|
| 0 | None (idle) | 4 | Thumb_Up |
| 1 | Closed_Fist | 5 | Thumb_Down |
| 2 | Open_Palm | 6 | Victory |
| 3 | Pointing_Up | 7 | ILoveYou |

Protocol: ASCII digit + newline (e.g. `b"4\n"`), sent PC → CPX only, on
debounced gesture *change* (not every frame).

## Purpose
**LEARN** 
To gain experience with
- developing wearable electronics
- computer vision
- embedded systems with low RAM
- microcontrollers
- combine creativity with engineering
- posting on linkedin
- markdown
- continual use of GitHub

Each Project will be to further my knowledge and get closer to the end goal


## WHY
- Make Fun Electronics and Enginerring project on my own
- If you are interested in electronics, you likely thought/think Iron Man is cool! (That is the case for me!) This is my way of making an Iron Man project and have my skills expand as I go.

## Projects in chronological order

| # | Project|
--------------
| 1 | Solid - Hello world of Computer Vision with MediaPipe |
| 2 | Heros - Add low cost RAM animations and slight customization with PILLOW |

## Requirements

- **Windows on ARM64** (or any platform where the native architecture lacks
  full MediaPipe/OpenCV wheel coverage) requires an **x64 Python install run
  under emulation** — see setup below. On native x64/x86_64 machines, skip
  the emulation step and just use a normal x64 Python install.
- **Python 3.11.6** — pinned specifically to avoid MediaPipe wheel
  availability issues on newer Python versions.
- An Adafruit **Circuit Playground Express**.
- A webcam.

## Setup

### 1. Install an x64 Python 3.11.6

On Windows ARM64 machines, install the **x64** build of Python (not ARM64) —
Windows runs x64 binaries transparently via emulation, and this is what
gives MediaPipe/OpenCV access to their full prebuilt-wheel coverage.

```powershell
winget install Python.Python.3.11 --architecture x64
```

Verify you actually got x64 after creating the venv (step 2):

```powershell
python -c "import platform; print(platform.machine())"
# should print: AMD64
```

If it prints `ARM64`, the venv was built from the wrong interpreter — delete
it and recreate using the explicit path to the x64 install.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

`requirements.txt`:

```
# Serial communication support
pyserial==3.5
# MediaPipe needs x64 architecture
# Using Python 3.11.6 to avoid MediaPipe wheel/version issues
mediapipe==0.10.32
opencv-python==4.13.0.92
opencv-contrib-python==4.13.0.92
numpy==2.4.3
```

MediaPipe pulls in its own supporting libraries (absl-py, flatbuffers,
sounddevice, etc.) automatically — no action needed.

### 4. Download the MediaPipe model file

If not included in repository, download the .task used in the project ex: gesture_recognizer.task

Can find it at
[Gesture Recognizer](https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb#scrollTo=OMjuVQiDYJKF) 

```
!wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task
```

### 5. Set up the CPX
> Example is using Solid project, can do same steps on the other projects

1. Copy `Solid/cpx/boot.py` and `Solid/cpx/code.py` to the CIRCUITPY drive
   (keep the names as-is — CircuitPython only auto-runs a file named exactly
   `code.py` or `main.py`).
2. **Power-cycle the board** (unplug/replug, or reset button) —
   `boot.py` only takes effect on a hard reset, not on save.
3. After reset, confirm the CPX shows **two** COM ports in Device Manager
   (Windows) — console first, data second. If only one appears, `boot.py`
   didn't take effect; repeat the power-cycle.

### 6. Set the CPX serial port

Open `Solid/pc/gesture_sender.py` and set `CPX_PORT` to your CPX's **data** CDC
port (not the console/REPL port):

```python
CPX_PORT = "COM3"   # <- change this to your port
```

**Finding your port:**
- Windows: Device Manager → Ports (COM & LPT) — look for two entries under
  the CPX; the data port is *OFTEN* higher-numbered one.
- Or run: `python -m serial.tools.list_ports -v`

Set `CPX_PORT = None` to fall back to automatic detection by USB VID
(`0x239A`) instead of hardcoding.

### 7. Run

```powershell
python Solid/pc/gesture_sender.py
```

Press `q` in the preview window to quit.


## T-SHIRT

1. Soldered on a side of brass sewable snaps on the back of each of the CPX pins
2. Attached the other side of the snaps on the pins I planned to use and added a little fabric glue
3. Pressed it against the t-shirt, and unsnapped the CPX away, leaving (most) of the pins I wanted to use for support
    - Had to redo this step a few times
    - 4 pins, and same 4 pins if CPX was positioned 180 degrees different, 2 at top and 2 at the bottom in odd-function positioning
    - Didn't use pins need for UART for future projects
4. Sewed on the snaps with regular thread and checked that the CPX fit correctly

## Notes on tooling

- **Pylint `E1101: Module 'cv2' has no member`** is a known false positive —
  `cv2` is a compiled C extension that Pylint can't statically introspect.
  `pyproject.toml` includes `extension-pkg-allow-list = ["cv2"]` to fix this,
  *provided* your linter is configured to run from the project's venv
  (`"pylint.importStrategy": "fromEnvironment"` in VS Code workspace
  settings). If Pylint is running against a different/global interpreter
  than the venv, no config here will resolve it — check which interpreter
  the linter is actually using first.

## Resources

- MediaPipe GestureRecognizer (task overview): https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer
- MediaPipe GestureRecognizer (Python API reference): https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python
- pyserial API reference: https://pyserial.readthedocs.io/en/latest/pyserial_api.html
- pyserial short intro (blocking vs. non-blocking reads): https://pyserial.readthedocs.io/en/latest/shortintro.html
- CircuitPython `usb_cdc` reference: https://docs.circuitpython.org/en/latest/shared-bindings/usb_cdc/index.html
- Adafruit Circuit Playground Express guide: https://learn.adafruit.com/adafruit-circuit-playground-express
