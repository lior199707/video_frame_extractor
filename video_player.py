import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import os
import threading
from extract_frames import extract_frames

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Extractor")
        self.root.geometry("1600x800")
        
        # Video variables
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.is_playing = False
        self.total_frames = 0
        self.fps = 0
        self.start_time = None
        self.end_time = None
        
        self.create_widgets()
        self.update_controls_state()
        
        # Bind keyboard shortcuts
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Left>', lambda e: self.skip_time(-5))
        self.root.bind('<Right>', lambda e: self.skip_time(5))
        self.root.bind('<Shift-Left>', lambda e: self.skip_time(-10))
        self.root.bind('<Shift-Right>', lambda e: self.skip_time(10))
        self.root.bind(',', lambda e: self.prev_frame())
        self.root.bind('.', lambda e: self.next_frame())

    def create_widgets(self):
        # Main container with two columns
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        
        # Left panel for video and basic controls
        left_panel = ttk.Frame(main_container)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Right panel for settings and output
        right_panel = ttk.Frame(main_container)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        
        # File selection frame (in left panel)
        file_frame = ttk.Frame(left_panel)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        file_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Choose Video File", command=self.select_file).grid(row=0, column=0, padx=(0, 10))
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, sticky="w")
        
        # Video display (in left panel)
        self.canvas = tk.Canvas(left_panel, width=960, height=540, bg='black')
        self.canvas.grid(row=1, column=0, pady=(0, 5))
        
        # Time display and slider (in left panel)
        time_frame = ttk.Frame(left_panel)
        time_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        time_frame.grid_columnconfigure(0, weight=1)
        
        self.time_label = ttk.Label(time_frame, text="00:00:00 / 00:00:00")
        self.time_label.pack()
        
        self.time_slider = ttk.Scale(time_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.time_slider.pack(fill=tk.X, pady=(5, 0))
        self.time_slider.bind("<ButtonRelease-1>", self.slider_changed)
        
        # Playback controls (in left panel)
        controls_frame = ttk.Frame(left_panel)
        controls_frame.grid(row=3, column=0, pady=(0, 5))
        
        ttk.Button(controls_frame, text="⏮ -10s", command=lambda: self.skip_time(-10)).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="⏮ -5s", command=lambda: self.skip_time(-5)).grid(row=0, column=1, padx=5)
        self.play_button = ttk.Button(controls_frame, text="▶", command=self.toggle_play)
        self.play_button.grid(row=0, column=2, padx=5)
        ttk.Button(controls_frame, text="⏭ +5s", command=lambda: self.skip_time(5)).grid(row=0, column=3, padx=5)
        ttk.Button(controls_frame, text="⏭ +10s", command=lambda: self.skip_time(10)).grid(row=0, column=4, padx=5)
        ttk.Button(controls_frame, text="◀ Frame", command=self.prev_frame).grid(row=0, column=5, padx=5)
        ttk.Button(controls_frame, text="Frame ▶", command=self.next_frame).grid(row=0, column=6, padx=5)
        
        # Instructions (in right panel)
        instructions = """
        Steps:
        1. Select a video file
        2. Navigate to desired start and end points
        3. Capture start and end times
        4. Set output folder name and interval
        5. Click Extract Frames to process
        """
        ttk.Label(right_panel, text=instructions, justify=tk.LEFT).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Time capture frame (in right panel)
        capture_frame = ttk.LabelFrame(right_panel, text="Time Capture")
        capture_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        capture_frame.grid_columnconfigure(1, weight=1)
        capture_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Button(capture_frame, text="Capture Start", command=self.capture_start).grid(row=0, column=0, padx=5, pady=5)
        self.start_label = ttk.Label(capture_frame, text="--:--:--")
        self.start_label.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(capture_frame, text="Capture End", command=self.capture_end).grid(row=0, column=2, padx=5, pady=5)
        self.end_label = ttk.Label(capture_frame, text="--:--:--")
        self.end_label.grid(row=0, column=3, padx=5, pady=5)
        
        # Extraction settings (in right panel)
        settings_frame = ttk.LabelFrame(right_panel, text="Extraction Settings")
        settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        settings_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(settings_frame, text="Output Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.folder_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.folder_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(settings_frame, text="Frame Interval:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.interval_var = tk.StringVar(value="60")
        ttk.Entry(settings_frame, textvariable=self.interval_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(settings_frame, text="Extract Frames", command=self.extract_frames).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Output display (in right panel)
        output_frame = ttk.LabelFrame(right_panel, text="Output Log")
        output_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 5))
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)
        
        self.output_text = tk.Text(output_frame, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar to output text
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=5)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure right panel to expand output
        right_panel.grid_rowconfigure(3, weight=1)

    def update_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            ("All files", "*.*")
        ])
        if file_path:
            self.video_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.load_video()
            self.update_controls_state()

    def load_video(self):
        if self.cap is not None:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(self.video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.time_slider.config(to=self.total_frames)
        self.update_frame()

    def update_frame(self):
        if self.cap is None:
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (960, 540))
            self.current_frame = ImageTk.PhotoImage(Image.fromarray(frame))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_frame)
            
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            current_time = current_frame / self.fps
            total_time = self.total_frames / self.fps
            
            self.time_label.config(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")
            self.time_slider.set(current_frame)
            
            if self.is_playing:
                self.root.after(int(1000/self.fps), self.update_frame)

    def toggle_play(self):
        if self.cap is None:
            return
        
        self.is_playing = not self.is_playing
        self.play_button.config(text="⏸" if self.is_playing else "▶")
        if self.is_playing:
            self.update_frame()

    def skip_time(self, seconds):
        if self.cap is None:
            return
        
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        new_frame = current_frame + (seconds * self.fps)
        new_frame = max(0, min(new_frame, self.total_frames))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        self.update_frame()

    def prev_frame(self):
        if self.cap is None:
            return
        
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, current_frame - 2))
        self.update_frame()

    def next_frame(self):
        if self.cap is None:
            return
        self.update_frame()

    def slider_changed(self, event):
        if self.cap is None:
            return
        
        frame_no = self.time_slider.get()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        self.update_frame()

    def capture_start(self):
        if self.cap is None:
            return
        
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.start_time = current_frame / self.fps
        self.start_label.config(text=self.format_time(self.start_time))

    def capture_end(self):
        if self.cap is None:
            return
        
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.end_time = current_frame / self.fps
        self.end_label.config(text=self.format_time(self.end_time))

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def extract_frames(self):
        if None in (self.video_path, self.start_time, self.end_time) or not self.folder_var.get():
            messagebox.showerror("Error", "Please select video, capture start/end times, and set output folder")
            return
        
        def run_extraction():
            try:
                self.output_text.delete(1.0, tk.END)
                self.update_output("Starting frame extraction...")
                
                # Run extraction with progress callback
                extract_frames(
                    self.video_path,
                    self.folder_var.get(),
                    int(self.interval_var.get()),
                    start_time=self.format_time(self.start_time),
                    end_time=self.format_time(self.end_time),
                    progress_callback=self.update_output
                )
                
                messagebox.showinfo("Success", "Frame extraction completed!")
                
            except Exception as e:
                self.update_output(f"\nError: {str(e)}")
                messagebox.showerror("Error", f"Failed to extract frames: {str(e)}")
        
        threading.Thread(target=run_extraction, daemon=True).start()

    def update_controls_state(self):
        state = 'normal' if self.cap is not None else 'disabled'
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Button, ttk.Entry, tk.Text)):
                try:
                    widget.config(state=state)
                except:
                    pass
        self.file_label.config(state='normal')
        
        # Keep file selection button always enabled
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget('text') == "Choose Video File":
                widget.config(state='normal')

    def __del__(self):
        if self.cap is not None:
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayer(root)
    root.mainloop()
