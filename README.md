# Video Frame Extractor

This application allows you to extract frames from a video file between specified start and end times at a given interval.

## Files

- `video_player.py`: The main script for the video frame extractor application.
- `extract_frames.py`: A utility script used by `video_player.py` to perform the frame extraction.

## How to Run

1. Ensure you have Python installed on your system.
2. Install the required libraries:
   ```bash
   pip install opencv-python pillow
   ```
3. Navigate to the `video_player_package` directory in your terminal.
4. Run the `video_player.py` script:
   ```bash
   python video_player.py
   ```
5. Follow the instructions in the application to select a video file, capture the start and end times, set the output folder and frame interval, and extract the frames.

## Keyboard Shortcuts

- **Spacebar:** Toggle play/pause.
- **Left Arrow:** Skip back 5 seconds.
- **Right Arrow:** Skip forward 5 seconds.
- **Shift + Left Arrow:** Skip back 10 seconds.
- **Shift + Right Arrow:** Skip forward 10 seconds.
- **, (comma):** Previous frame.
- **. (period):** Next frame.
