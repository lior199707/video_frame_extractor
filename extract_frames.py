import cv2
import os
import argparse
from pathlib import Path
import re
import sys

def time_to_seconds(time_str):
    """
    Convert time string in mm:ss format to seconds
    
    Args:
        time_str (str): Time in mm:ss format
        
    Returns:
        float: Time in seconds
    """
    if not time_str:
        return None
        
    match = re.match(r'^(\d+):(\d{2})$', time_str)
    if not match:
        raise ValueError("Time must be in mm:ss format (e.g., 1:30)")
        
    minutes, seconds = map(int, match.groups())
    return minutes * 60 + seconds

def extract_frames(video_path, output_folder, frame_interval, start_time='0:00', end_time=None, progress_callback=None):
    """
    Extract frames from a video file at specified intervals
    
    Args:
        video_path (str): Path to the video file
        output_folder (str): Path to save extracted frames
        frame_interval (int): Number of frames to skip between extractions
        start_time (float): Start time in seconds (default: 0)
        end_time (float): End time in seconds (default: None, process until end)
        progress_callback (callable): Optional callback function for progress updates
    """
    START_CROP_Y = 140
    END_CROP_Y = 668
    START_CROP_X = 649
    END_CROP_X = 1596
    RESIZE_DIM = (1024, 512) # (new x dim, new y dim)

    # Create or clear output directory
    output_path = Path(output_folder)
    if output_path.exists():
        print(f"\nClearing existing contents of {output_folder}")
        for file in output_path.glob('*'):
            try:
                file.unlink()
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")
    else:
        print(f"\nCreating output directory: {output_folder}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError("Error: Could not open video file")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    print("\nVideo Information:")
    print(f"FPS: {fps:.2f}")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Extracting every {frame_interval} frames")
    print(f"Output directory: {output_folder}")
    print("\nStarting frame extraction...")
    
    frame_count = 0
    saved_count = 0
    
    # Convert time strings to seconds
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    
    # Convert times to frame numbers
    start_frame = int(start_seconds * fps) if start_seconds is not None else 0
    end_frame = int(end_seconds * fps) if end_seconds is not None else total_frames

    # Calculate total frames to process
    total_frames_to_process = end_frame - start_frame

    # Seek to start position
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_count = start_frame

    while frame_count < end_frame:
        ret, frame = cap.read()
        
        if not ret:
            break
            
        if (frame_count - start_frame) % frame_interval == 0:
            # Crop and resize frame
            cropped_frame = frame[START_CROP_Y:END_CROP_Y, START_CROP_X:END_CROP_X]
            resized_frame = cv2.resize(cropped_frame, RESIZE_DIM, interpolation=cv2.INTER_CUBIC)

            # Save frame as image
            output_path = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
            cv2.imwrite(output_path, resized_frame)
            saved_count += 1
            
            # Calculate and report progress
            progress = (frame_count - start_frame) / total_frames_to_process * 100
            status = f"Processing frame {frame_count:06d} ({progress:.1f}%) - Saved to {output_path}"
            print(status)
            
            if progress_callback:
                progress_callback(status)
            
        frame_count += 1
        
    cap.release()
    
    final_status = f"\nExtraction complete!\nExtracted {saved_count} frames to {output_folder}\nProcessing rate: {(saved_count/total_frames_to_process)*100:.1f}% of total frames"
    print(final_status)
    if progress_callback:
        progress_callback(final_status)

def main():
    parser = argparse.ArgumentParser(
        description='Extract frames from a video file',
        epilog='Example: python extract_frames.py video.mp4 output_frames --interval 5 --start 1:30 --end 2:45'
    )
    parser.add_argument('video_path', type=str, help='Path to the video file')
    parser.add_argument('output_folder', type=str, help='Folder to save extracted frames')
    parser.add_argument('--interval', type=int, default=60,
                        help='Extract every Nth frame (default: 5)')
    parser.add_argument('--start', type=str, default='0:00',
                        help='Start time in mm:ss format (default: 0:00)')
    parser.add_argument('--end', type=str, default=None,
                        help='End time in mm:ss format (default: process until end)')
    
    args = parser.parse_args()
    
    extract_frames(args.video_path, args.output_folder, args.interval, 
                  start_time=args.start, end_time=args.end)

if __name__ == "__main__":
    main()
