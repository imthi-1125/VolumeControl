# main.py
import cv2
import math
import numpy as np
import time
from collections import deque

from utils.hand_detector import HandDetector
from utils.volume_control import VolumeController

# -----------------------------
# Config
# -----------------------------
SMOOTHING_WINDOW = 5
MUTE_DEBOUNCE_SECONDS = 0.8
VOLUME_CHANGE_THRESHOLD = 1
SHOW_INSTRUCTIONS = True

# -----------------------------
# Initialize
# -----------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam. Check camera permissions.")

detector = HandDetector(maxHands=1, detectionCon=0.6, trackCon=0.6)
vol_ctrl = VolumeController(minDist=30, maxDist=300)

percent_history = deque(maxlen=SMOOTHING_WINDOW)
muted = False
fist_start_time = None
last_mute_action_time = 0
calibrated = False
calib_msg_time = 0

def fingers_up_count(lmList):
    if not lmList or len(lmList) < 21:
        return 0
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    count = 0
    for tip, pip in zip(tips, pips):
        if lmList[tip][1] < lmList[pip][1]:
            count += 1
    return count

def draw_ui(frame, vol_percent, vol_ctrl_obj, msg=None):
    h, w, _ = frame.shape
    x1, y1 = 50, 150
    x2, y2 = 85, 400
    cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 100, 100), 3)
    bar_y = int(np.interp(vol_percent, [0, 100], [y2, y1]))
    cv2.rectangle(frame, (x1+3, bar_y), (x2-3, y2-3), (0, 200, 0), -1)
    cv2.putText(frame, f'{vol_percent} %', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 2)
    cv2.putText(frame, f'Cal min:{vol_ctrl_obj.minDist} max:{vol_ctrl_obj.maxDist}', (130, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    if SHOW_INSTRUCTIONS:
        lines = [
            "Instructions:",
            " - Move thumb & index to change volume.",
            " - Press 'c' to set MIN distance.",
            " - Press 'o' to set MAX distance.",
            " - Press 'r' to reset defaults.",
            " - Closed fist -> mute (hold 0.8s).",
            " - ESC -> quit"
        ]
        for i, line in enumerate(lines):
            cv2.putText(frame, line, (130, 60 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180,180,180), 1)

    if msg:
        cv2.putText(frame, msg, (40, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

# -----------------------------
# Main loop
# -----------------------------
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame)

        current_percent = 0

        if lmList and len(lmList) >= 9:
            x1, y1 = lmList[4]
            x2, y2 = lmList[8]

            cv2.circle(frame, (x1, y1), 8, (255, 0, 0), -1)
            cv2.circle(frame, (x2, y2), 8, (0, 255, 0), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

            distance = math.hypot(x2 - x1, y2 - y1)
            if calibrated and time.time() - calib_msg_time < 1.8:
                calib_msg = "Calibrated!"
            else:
                calib_msg = None

            current_percent = vol_ctrl.distance_to_percent(distance)
            percent_history.append(current_percent)
            smooth_percent = int(np.mean(percent_history))

            if not muted and (abs(smooth_percent - (percent_history[-2] if len(percent_history)>1 else -999)) >= VOLUME_CHANGE_THRESHOLD):
                vol_ctrl.set_volume_percent(smooth_percent)

            fingers_up = fingers_up_count(lmList)
            if fingers_up == 0:
                if fist_start_time is None:
                    fist_start_time = time.time()
                else:
                    held = time.time() - fist_start_time
                    if held >= MUTE_DEBOUNCE_SECONDS and (time.time() - last_mute_action_time) > MUTE_DEBOUNCE_SECONDS:
                        muted = not muted
                        vol_ctrl.set_mute(muted)
                        last_mute_action_time = time.time()
            else:
                fist_start_time = None

            draw_ui(frame, smooth_percent, vol_ctrl, msg=calib_msg)
        else:
            draw_ui(frame, int(np.mean(percent_history)) if percent_history else 0, vol_ctrl)

        cv2.imshow("Gesture Volume (macOS) - BOSS", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break
        if key == ord('c'):
            if lmList and len(lmList) >= 9:
                d = int(math.hypot(lmList[8][0]-lmList[4][0], lmList[8][1]-lmList[4][1]))
                vol_ctrl.minDist = d
                calibrated = True
                calib_msg_time = time.time()
        if key == ord('o'):
            if lmList and len(lmList) >= 9:
                d = int(math.hypot(lmList[8][0]-lmList[4][0], lmList[8][1]-lmList[4][1]))
                vol_ctrl.maxDist = d
                calibrated = True
                calib_msg_time = time.time()
        if key == ord('r'):
            vol_ctrl.minDist = 30
            vol_ctrl.maxDist = 300
            calibrated = False

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Exiting, BOSS.")
