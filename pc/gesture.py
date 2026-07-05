import cv2
import mediapipe as mp
import time
import math

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = "gesture_recognizer.task"
CAMERA_ID  = 0
FONT       = cv2.FONT_HERSHEY_SIMPLEX
