import mss
import numpy as np
import time
from pynput.mouse import Button, Controller
import keyboard

coords = [725, 860, 1025, 1160]
mouse = Controller()

while True:
    speed = input("What speed multiplier will you use (answer 1, 2 or 4)? ")
    if speed == "1":
        DELAY_MS = 1280
        MIN_DETECTION_DELAY_MS = 175
        break
    elif speed == "2":
        DELAY_MS = 700
        MIN_DETECTION_DELAY_MS = 130
        break
    elif speed == "4":
        DELAY_MS = 320
        MIN_DETECTION_DELAY_MS = 100
        break
    else:
        print(f"Speed multiplier {speed} is not in the right format or not supported")

print(f"Starting bot with speed multiplier {speed}x")


def is_whiteish(b, g, r):
    return b >= 200 and g >= 200 and r >= 200

platforms = []  # list of {x, detected_at}
last_detected_in_lane = {x: 0 for x in coords}

with mss.mss() as sct:
    while True:
        if keyboard.is_pressed('esc'):
            break

        now = time.time() * 1000

        to_keep = []
        for p in platforms:
            if now - p["detected_at"] >= DELAY_MS:
                mouse.position = (p["x"], 800)
                mouse.click(Button.left, 1)
            else:
                to_keep.append(p)
        platforms = to_keep

        # Screenshot detection region
        left = min(coords)
        right = max(coords)
        width = right - left + 1
        monitor = {
            "top": 90,
            "left": left,
            "width": width,
            "height": 120 - 90 + 1
        }
        screenshot = np.array(sct.grab(monitor))

        for x in coords:
            x_offset = x - left
            detected = False
            whiteish_hits = 0

            for y in range(0, 120 - 90 + 1):
                b, g, r, _ = screenshot[y, x_offset]
                if is_whiteish(b, g, r):
                    whiteish_hits += 1
                if whiteish_hits >= 5:
                    detected = True
                    break

            if detected and (now - last_detected_in_lane[x] >= MIN_DETECTION_DELAY_MS):
                platforms.append({"x": x, "detected_at": now})
                last_detected_in_lane[x] = now
