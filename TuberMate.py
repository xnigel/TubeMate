import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import json
import os
import queue
import re
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable, PytubeError

# Global variables and configurations
CONFIG_FILE = "config.json"
MAX_WORKERS = 8
DEFAULT_CONFIG = {
    "download_path": os.path.expanduser("~"),
    "format": "mp3",
    "resolution": "720p",
    "audio_bitrate": "128kbps"
}
resolutions = ["1080p", "720p", "480p", "360p", "240p", "144p"]
audio_bitrates = ["320kbps", "256kbps", "192kbps", "128kbps", "64kbps"]

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Bulk Downloader")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.download_queue = queue.Queue()
        self.download_threads = []
        self.current_downloads = 0

        self.config = self.load_config()

        self.setup_ui()
        self.load_settings_into_ui()

    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top settings section
        settings_frame = tk.LabelFrame(main_frame, text="Settings", padx=10, pady=10, bg="#ffffff")
        settings_frame.pack(fill=tk.X, pady=10)

        # Download path
        path_frame = tk.Frame(settings_frame, bg="#ffffff")
        path_frame.pack(fill=tk.X, pady=5)
        tk.Label(path_frame, text="Download Path:", bg="#ffffff").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(path_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(path_frame, text="Select", command=self.select_path).pack(side=tk.LEFT)
        tk.Button(path_frame, text="Export Settings", command=self.export_config).pack(side=tk.LEFT, padx=5)

        # Format and quality options
        options_frame = tk.Frame(settings_frame, bg="#ffffff")
        options_frame.pack(fill=tk.X, pady=5)

        tk.Label(options_frame, text="Format:", bg="#ffffff").pack(side=tk.LEFT)
        self.format_var = tk.StringVar()
        self.mp3_button = tk.Button(options_frame, text="MP3", command=lambda: self.set_format_and_style("mp3"))
        self.mp3_button.pack(side=tk.LEFT, padx=5)
        self.mp4_button = tk.Button(options_frame, text="MP4", command=lambda: self.set_format_and_style("mp4"))
        self.mp4_button.pack(side=tk.LEFT, padx=5)

        tk.Label(options_frame, text="Resolution/Bitrate:", bg="#ffffff").pack(side=tk.LEFT, padx=(20, 0))
        self.quality_var = tk.StringVar()
        self.quality_menu = ttk.Combobox(options_frame, textvariable=self.quality_var, state="readonly", width=10)
        self.quality_menu.pack(side=tk.LEFT, padx=5)

        # URL input area (now with 8 separate boxes)
        url_frame = tk.LabelFrame(main_frame, text="Add Video Links", padx=10, pady=10, bg="#ffffff")
        url_frame.pack(fill=tk.X, pady=10)
        tk.Label(url_frame, text="Enter up to 8 YouTube Links:", bg="#ffffff").pack(anchor=tk.W)
        
        self.url_entries = []
        for i in range(MAX_WORKERS):
            entry = tk.Entry(url_frame, width=70)
            entry.pack(fill=tk.X, pady=2)
            self.url_entries.append(entry)

        tk.Button(url_frame, text="Add Tasks", command=self.add_tasks, bg="#4CAF50", fg="white").pack(pady=5)

        # Task list area
        tasks_frame = tk.LabelFrame(main_frame, text="Download Tasks", padx=10, pady=10, bg="#ffffff")
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.task_canvas = tk.Canvas(tasks_frame, bg="#ffffff")
        self.task_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(tasks_frame, orient="vertical", command=self.task_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.task_container = tk.Frame(self.task_canvas, bg="#ffffff")
        self.task_canvas.create_window((0, 0), window=self.task_container, anchor="nw")

        self.task_container.bind("<Configure>", lambda e: self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all")))

        # Menu bar
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Configuration", command=self.export_config)
        file_menu.add_command(label="Import Configuration", command=self.import_config)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def set_format_and_style(self, format_type):
        """Sets the format variable and updates button styles."""
        self.format_var.set(format_type)
        if format_type == "mp3":
            self.mp3_button.config(bg="#4CAF50", fg="white")
            self.mp4_button.config(bg="#ffffff", fg="black")
        else:
            self.mp3_button.config(bg="#ffffff", fg="black")
            self.mp4_button.config(bg="#4CAF50", fg="white")
        self.update_options()
    
    def load_settings_into_ui(self):
        """Load configuration into UI"""
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.config["download_path"])
        
        # Set format and style based on loaded config
        self.set_format_and_style(self.config["format"])

        if self.config["format"] == "mp4":
            self.quality_var.set(self.config["resolution"])
        else:
            self.quality_var.set(self.config["audio_bitrate"])

    def update_options(self):
        """Update dropdown options based on format"""
        selected_format = self.format_var.get()
        if selected_format == "mp4":
            self.quality_menu["values"] = resolutions
            self.quality_var.set(self.config["resolution"])
        else:
            self.quality_menu["values"] = audio_bitrates
            self.quality_var.set(self.config["audio_bitrate"])

    def extract_video_id(self, url):
        """Extract the video ID from a YouTube URL"""
        pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/|youtube-nocookie\.com\/(?:watch\?v=))([\w-]{11})"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def select_path(self):
        """Select download path"""
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.config["download_path"] = path

    def add_tasks(self):
        """Add tasks from the text box to the queue"""
        urls = [entry.get().strip() for entry in self.url_entries]
        for url in urls:
            if url:
                video_id = self.extract_video_id(url)
                if not video_id:
                    messagebox.showerror("Invalid Link", f"Could not extract video ID from link: {url}")
                    continue
                
                standard_url = f"https://www.youtube.com/watch?v={video_id}"
                try:
                    yt = YouTube(standard_url)
                    task_info = {
                        "url": standard_url,
                        "title": yt.title,
                        "format": self.format_var.get(),
                        "quality": self.quality_var.get(),
                        "path": self.path_entry.get()
                    }
                    self.download_queue.put(task_info)
                    self.create_task_ui(task_info)
                    self.start_next_download()
                except PytubeError as e:
                    messagebox.showerror("Download Error", f"Pytube encountered an error: {e}")
                except Exception as e:
                    messagebox.showerror("Invalid Link", f"An unexpected error occurred while parsing the link: {standard_url}\nError: {e}")


    def create_task_ui(self, task_info):
        """Create UI elements for each task"""
        task_frame = tk.Frame(self.task_container, padx=10, pady=5, bg="#f9f9f9", bd=1, relief="solid")
        task_frame.pack(fill=tk.X, pady=2, padx=5)

        title_label = tk.Label(task_frame, text=task_info["title"], anchor="w", bg="#f9f9f9")
        title_label.pack(fill=tk.X)

        progress_bar = ttk.Progressbar(task_frame, orient="horizontal", length=100, mode="determinate")
        progress_bar.pack(fill=tk.X)

        status_label = tk.Label(task_frame, text="Pending...", anchor="w", bg="#f9f9f9")
        status_label.pack(fill=tk.X)

        task_info["frame"] = task_frame
        task_info["progress_bar"] = progress_bar
        task_info["status_label"] = status_label

    def start_next_download(self):
        """Start the next download task (if there are free threads)"""
        if self.current_downloads < MAX_WORKERS and not self.download_queue.empty():
            task = self.download_queue.get()
            self.current_downloads += 1
            thread = threading.Thread(target=self.download_video, args=(task,))
            thread.start()
            self.download_threads.append(thread)

    def download_video(self, task):
        """Handle single video download"""
        task["status_label"].config(text="Downloading...")
        
        try:
            yt = YouTube(task["url"], on_progress_callback=lambda stream, chunk, bytes_remaining: self.update_progress(task, stream, bytes_remaining))
            
            stream_to_download = None
            if task["format"] == "mp4":
                # Find the best stream based on resolution preference
                for res in resolutions:
                    stream_to_download = yt.streams.filter(res=res, progressive=True).first()
                    if stream_to_download:
                        break
                if not stream_to_download:
                    stream_to_download = yt.streams.get_highest_resolution()
                    task["status_label"].config(text=f"Selected resolution not found, downloading highest resolution MP4...")
            else: # mp3
                # Find the best stream based on bitrate preference
                for abr in audio_bitrates:
                    stream_to_download = yt.streams.filter(only_audio=True, abr=abr).first()
                    if stream_to_download:
                        break
                if not stream_to_download:
                    stream_to_download = yt.streams.filter(only_audio=True).first()
                    task["status_label"].config(text=f"Selected bitrate not found, downloading highest bitrate MP3...")

            if stream_to_download:
                file_path = stream_to_download.download(output_path=task["path"])
                
                # For MP3, rename the file
                if task["format"] == "mp3":
                    base, ext = os.path.splitext(file_path)
                    new_file = base + '.mp3'
                    os.rename(file_path, new_file)
                
                task["status_label"].config(text="Complete!", fg="green")
                task["progress_bar"]["value"] = 100
            else:
                task["status_label"].config(text="Failed: No downloadable stream found", fg="red")
        except Exception as e:
            task["status_label"].config(text=f"Download failed: {e}", fg="red")
        finally:
            self.current_downloads -= 1
            self.root.after(100, self.start_next_download)

    def update_progress(self, task, stream, bytes_remaining):
        """Update task progress bar"""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        task["progress_bar"]["value"] = percentage_of_completion
        self.root.update_idletasks()

    def export_config(self):
        """Export configuration to JSON file"""
        self.config["download_path"] = self.path_entry.get()
        self.config["format"] = self.format_var.get()
        if self.config["format"] == "mp4":
            self.config["resolution"] = self.quality_var.get()
        else:
            self.config["audio_bitrate"] = self.quality_var.get()
            
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
        messagebox.showinfo("Configuration Export", "Configuration successfully exported to config.json")

    def import_config(self):
        """Import configuration from JSON file"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self.load_settings_into_ui()
            messagebox.showinfo("Configuration Import", "Configuration successfully imported")
        except FileNotFoundError:
            messagebox.showerror("Configuration Import", "Configuration file config.json not found")
        except json.JSONDecodeError:
            messagebox.showerror("Configuration Import", "Configuration file format error")

    def load_config(self):
        """Load configuration on startup"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                return DEFAULT_CONFIG
        return DEFAULT_CONFIG

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
