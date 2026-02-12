#!/usr/bin/env python3
"""main.py — Robust runner for object counting/tracking."""

import os
import sys
import glob
import cv2
import numpy as np
import datetime
from tracker import CentroidTracker
from object_counter import ObjectCounter

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_input_video():
    candidates = [
        os.path.join(SCRIPT_DIR, "Videos", "input.mp4"),
        os.path.join(SCRIPT_DIR, "videos", "input.mp4"),
        os.path.join(SCRIPT_DIR, "input.mp4")
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    for ext in ("*.mp4", "*.avi", "*.mov", "*.mkv"):
        matches = glob.glob(os.path.join(SCRIPT_DIR, "Videos", ext))
        if matches:
            return sorted(matches)[0]  # Return the first match alphabetically
    return None

def get_timestamped_filename(extension="avi"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(SCRIPT_DIR, "output", f"result_{timestamp}.{extension}")

def main():
    video_path = None
    output_path = None
    test_mode = False
    test_frames = 100
    output_format = "avi"

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg == "--test":
            test_mode = True
        elif arg.startswith("--test-frames="):
            try:
                test_frames = int(arg.split("=", 1)[1])
            except Exception:
                pass
        elif arg.startswith("--output="):
            output_path = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1].lower()
        else:
            video_path = arg

    os.makedirs(os.path.join(SCRIPT_DIR, "Videos"), exist_ok=True)
    os.makedirs(os.path.join(SCRIPT_DIR, "output"), exist_ok=True)

    if not video_path and not test_mode:
        found = find_input_video()
        if found:
            video_path = found
            print(f"Using video file: {video_path}")
        else:
            print("No input video found. Falling back to webcam (device 0).")
            video_path = 0

    cap = None
    frame = None
    if not test_mode:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video file '{video_path}'")
            sys.exit(1)
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Unable to read first frame from '{video_path}'")
            cap.release()
            sys.exit(1)
    else:
        frame_h, frame_w = 480, 640
        frame = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)

    frame_h, frame_w = frame.shape[:2]
    if output_format == "mp4":
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    else:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

    if not output_path:
        output_path = get_timestamped_filename(extension=output_format)

    out = cv2.VideoWriter(output_path, fourcc, 30.0, (frame_w, frame_h))
    show_windows = not test_mode

    ct = CentroidTracker()
    counter = ObjectCounter(line_position=min(300, frame_h - 1))
    fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

    if test_mode:
        for i in range(test_frames):
            frame = frame.copy()
            x = 10 + (i * 5) % (frame_w - 60)
            cv2.rectangle(frame, (x, 200), (x + 40, 260), (255, 255, 255), -1)

            fgmask = fgbg.apply(frame)
            _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            rects = []
            for c in contours:
                if cv2.contourArea(c) < 100:
                    continue
                x, y, w, h = cv2.boundingRect(c)
                rects.append((x, y, w, h))

            objects = ct.update(rects)
            count = counter.update(objects)

            cv2.line(frame, (0, counter.line_position), (frame_w, counter.line_position), (0, 255, 0), 2)
            for (objectID, centroid) in objects.items():
                cx, cy = centroid
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(frame, f"ID {objectID}", (cx - 15, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            cv2.putText(frame, f"Count: {count}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            out.write(frame)

        out.release()
        print(f"Test run completed — output saved to '{output_path}'")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fgmask = fgbg.apply(frame)
        _, fgmask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        rects = []
        for c in contours:
            if cv2.contourArea(c) < 1000:
                continue
            x, y, w, h = cv2.boundingRect(c)
            rects.append((x, y, w, h))

        objects = ct.update(rects)
        count = counter.update(objects)

        cv2.line(frame, (0, counter.line_position), (frame_w, counter.line_position), (0, 255, 0), 2)
        for (objectID, centroid) in objects.items():
            cx, cy = centroid
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"ID {objectID}", (cx - 15, cy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        cv2.putText(frame, f"Count: {count}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        if show_windows:
            cv2.imshow("Frame", frame)
            cv2.imshow("Mask", fgmask)

        out.write(frame)

        if show_windows and (cv2.waitKey(30) & 0xFF == 27):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video processing completed — output saved to '{output_path}'")

if __name__ == "__main__":
    main()