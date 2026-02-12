**Project Overview**: This repository implements a simple object counting and tracking pipeline using OpenCV background subtraction and a centroid-based tracker. It reads a video or webcam feed, detects moving objects, assigns IDs, and counts objects crossing a horizontal line.

**Prerequisites**:
- **Python**: 3.8+ installed and on PATH.
- **Packages**: install `opencv-python` and `numpy`.

Install dependencies (PowerShell):

```powershell
python -m pip install --upgrade pip
pip install opencv-python numpy
```

**Files**:
- **main.py**: Runner script — discovers input video, falls back to webcam, or runs a headless synthetic `--test` mode. Writes output to `output/result.avi` by default.
- **tracker.py**: `CentroidTracker` implementation (register/deregister, match centroids, handle disappearances).
- **object_counter.py**: `ObjectCounter` that increments the count when centroid crosses the configured `line_position`.
- **Videos/**: place input videos here (optional).
- **output/**: output videos (created automatically).

**Quick Usage** (PowerShell):

- Auto-discover or webcam (if no file present):

```powershell
python .\main.py
```

- Run with a specific video file (recommended — wrap path in quotes if it contains spaces):

```powershell
python .\main.py "C:\full\path\to\your video.mp4"
```

- Headless synthetic test mode (no GUI, writes `output/result.avi`):

```powershell
python .\main.py --test --test-frames=100
```

**Command-line behavior**:
- If you pass a path it uses that file.
- If no path is passed it attempts to find `Videos/input.mp4`, `videos/input.mp4` or any common video files in `Videos/` or the current folder.
- If no file is found and not in `--test` mode, the script falls back to the default webcam (device 0).

**Configuration**:
- Adjust the counting line by editing the `line_position` argument passed to `ObjectCounter` in `main.py`.
- Tune the background subtractor parameters in `main.py` (`history`, `varThreshold`) and the contour area threshold (`min contour area`) to match your scene.

**Troubleshooting**:
- If `VideoWriter` fails to write or output is blank, ensure the script can read at least one frame (valid video path or working webcam). The code reads the first frame and uses its size to create the writer.
- If `cv2.imshow` windows do not appear, make sure you run the script in an environment with a display (not headless) and that OpenCV has GUI support.
- If tracking seems unstable, try lowering the `min contour area` or adjusting `varThreshold` and `history` for `createBackgroundSubtractorMOG2`.

**Next steps / Enhancements** (suggestions):
- Add CLI flags for `--min-area`, `--fps`, `--output`, and `--no-write`.
- Add a requirements.txt and optional virtual environment instructions.
- Add unit tests for tracker logic and a small sample video for integration tests.

If you want, I can add CLI flags next or move a provided video into `Videos/` and run a full test; tell me which you prefer.
