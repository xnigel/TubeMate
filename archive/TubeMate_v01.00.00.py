import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import json
import os
import queue
import re
import base64
import yt_dlp

# Global variables and configurations
CONFIG_FILE = "config.json"
MAX_WORKERS = 4
DEFAULT_CONFIG = {
    "download_path": os.path.expanduser("~"),
    "format": "mp3",
    "resolution": "720p",
    "audio_bitrate": "128kbps"
}
resolutions = ["1080p", "720p", "480p", "360p", "240p", "144p"]
audio_bitrates = ["320kbps", "256kbps", "192kbps", "128kbps", "64kbps"]

# The icon is commented out to avoid errors since its base64 string is not provided
ICON_PNG_BASE64 = """
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cGUvUmVzb3VyY2VFdmVudCMiCiAgICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOkdJTVA9Imh0dHA6Ly93d3cuZ2ltcC5vcmcveG1wLyIKICAgIHhtbG5zOmlwdGNFeHQ9Imh0dHA6Ly9pcHRjLm9yZy9zdGQvSXB0YzR4bXBFeHQvMjAwOC0wMi0yOS8iCiAgICB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgeG1wTU06RG9jdW1lbnRJRD0iZ2ltcDpkb2NpZDpnaW1wOmE4MzRhNmI1LWQyMDAtNGEzZC05NWZmLTI2ODlkNzIzOTlkMCIKICAgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDphNDczZjIyNy02MTAwLTQ3NTAtOGI4OC00NDUyMzkyOWQxOWMiCiAgIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDoxZTkwM2UyNy1jZmMwLTQ4NzAtYjE0Mi1mZTI4MjczMTQ3YTAiCiAgIGRjOkZvcm1hdD0iaW1hZ2UvcG5nIgogICBleGlmOkRhdGVUaW1lT3JpZ2luYWw9IjIwMjUtMDktMDNUMDY6Mzk6MTArMDA6MDAiCiAgIEdJTVA6QVBJPSIyLjAiCiAgIEdJTVA6UGxhdGZvcm09IldpbmRvd3MiCiAgIEdJTVA6VGltZVN0YW1wPSIxNzU2ODgxODY3NzE2MTExIgogICBHSU1QOlZlcnNpb249IjIuMTAuMzAiCiAgIGlwdGNFeHQ6RGlnaXRhbFNvdXJjZUZpbGVUeXBlPSJodHRwOi8vY3YuaXB0Yy5vcmcvbmV3c2NvZGVzL2RpZ2l0YWxzb3VyY2V0eXBlL2NvbXBvc2l0ZVdpdGhUcmFpbmVkQWxnb3JpdGhtaWNNZWRpYSIKICAgaXB0Y0V4dDpEaWdpdGFsU291cmNlVHlwZT0iaHR0cDovL2N2LmlwdGMub3JnL25ld3Njb2Rlcy9kaWdpdGFsc291cmNldHlwZS9jb21wb3NpdGVXaXRoVHJhaW5lZEFsZ29yaXRobWljTWVkaWEiCiAgIHBob3Rvc2hvcDpDcmVkaXQ9IkVkaXRlZCB3aXRoIEdvb2dsZSBBSSIKICAgcGhvdG9zaG9wOkRhdGVDcmVhdGVkPSIyMDI1LTA5LTAzVDA2OjM5OjEwKzAwOjAwIgogICB0aWZmOk9yaWVudGF0aW9uPSIxIgogICB4bXA6Q3JlYXRvclRvb2w9IkdJTVAgMi4xMCI+CiAgIDx4bXBNTTpIaXN0b3J5PgogICAgPHJkZjpTZXE+CiAgICAgPHJkZjpsaQogICAgICBzdEV2dDphY3Rpb249InNhdmVkIgogICAgICBzdEV2dDpjaGFuZ2VkPSIvIgogICAgICBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjllMmQxYTUwLTcyMWEtNDU1MC05Y2RkLTA2ZmM0ZDJiYTQ3OCIKICAgICAgc3RFdnQ6c29mdHdhcmVBZ2VudD0iR2ltcCAyLjEwIChXaW5kb3dzKSIKICAgICAgc3RFdnQ6d2hlbj0iMjAyNS0wOS0wM1QxNjo0MjoyNCIvPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJzYXZlZCIKICAgICAgc3RFdnQ6Y2hhbmdlZD0iLyIKICAgICAgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpkZmMxZjVmOC00NTIxLTQ5YzMtODA0YS03ODMzYzY4NThhMTkiCiAgICAgIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkdpbXAgMi4xMCAoV2luZG93cykiCiAgICAgIHN0RXZ0OndoZW49IjIwMjUtMDktMDNUMTY6NDQ6MjciLz4KICAgIDwvcmRmOlNlcT4KICAgPC94bXBNTTpIaXN0b3J5PgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg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
"""

class TubeMate:
    def __init__(self, root):
        self.root = root
        root.title("TubeMate")
        ver = "01.00.00"
        yr = "2025.09.08"
        root.title('TubeMate' + " (v" + ver +")" + " - " + yr + " - Nigel Zhai")
        root.geometry("500x600")
        root.minsize(500,600)
        root.maxsize(500,600)
        root.configure(bg="#f0f0f0")

        self.set_window_icon()

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

        # Frame 1 - Settings
        settings_frame = tk.LabelFrame(main_frame, text="Settings", padx=10, pady=10, bg="#f0f0f0")
        settings_frame.pack(fill=tk.X, pady=10)

        self.lable_path = tk.Label(settings_frame, text="Directory:", bg="#f0f0f0")
        self.lable_path.grid(row=0, column=0, padx=5, pady=5, sticky="E")

        self.path_entry = tk.Entry(settings_frame, width=50)
        self.path_entry.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky="WE")

        self.button_select = tk.Button(settings_frame, text="Select", command=self.select_path)
        self.button_select.grid(row=0, column=5, padx=5, pady=5, sticky="W")

        tk.Label(settings_frame, text="Format:", bg="#f0f0f0").grid(row=1, column=0, padx=(0, 5), pady=5, sticky="E")
        self.format_var = tk.StringVar()

        self.mp3_button = tk.Button(settings_frame, text="MP3", width=5, command=lambda: self.set_format_and_style("mp3"))
        self.mp3_button.grid(row=1, column=1, padx=5, pady=5, sticky="W")

        self.mp4_button = tk.Button(settings_frame, text="MP4", width=5, command=lambda: self.set_format_and_style("mp4"))
        self.mp4_button.grid(row=1, column=2, padx=5, pady=5, sticky="W")

        tk.Label(settings_frame, text="Resolution/Bitrate:", bg="#f0f0f0").grid(row=1, column=3, padx=(20, 5), pady=5, sticky="W")
        self.quality_var = tk.StringVar()

        self.quality_menu = ttk.Combobox(settings_frame, textvariable=self.quality_var, state="readonly", width=10)
        self.quality_menu.grid(row=1, column=4, padx=5, pady=5, sticky="W")

        # Frame 2 - URL input area
        url_frame = tk.LabelFrame(main_frame, text="Add Video Links", padx=10, pady=10, bg="#f0f0f0")
        url_frame.pack(fill=tk.X, pady=10)

        tk.Label(url_frame, text="Enter up to 8 YouTube Links:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="W")

        self.url_entries = []
        for i in range(MAX_WORKERS):
            entry = tk.Entry(url_frame, width=70)
            entry.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
            self.url_entries.append(entry)

            # Add paste button for each row
            paste_button = tk.Button(url_frame, text="Paste", command=lambda e=entry: self.paste_from_clipboard(e))
            paste_button.grid(row=i+1, column=1, padx=5, pady=2, sticky="ew")

        url_frame.grid_columnconfigure(0, weight=1)

        tk.Button(url_frame, text="Go!", width=10, command=self.add_tasks, bg="#4CAF50", fg="white").grid(row=MAX_WORKERS + 1, column=0, pady=5)

        # Frame 3 - Task list area
        tasks_frame = tk.LabelFrame(main_frame, text="Download Tasks", padx=10, pady=10, bg="#f0f0f0")
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

    def paste_from_clipboard(self, entry_widget):
        """Paste clipboard content into given entry"""
        try:
            text = self.root.clipboard_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, text)
        except tk.TclError:
            messagebox.showwarning("Clipboard", "Clipboard is empty or not text.")

    def set_window_icon(self):
        try:
            icon_data = base64.b64decode(ICON_PNG_BASE64)
            try:
                photo_image = tk.PhotoImage(data=icon_data)
                self.root.iconphoto(True, photo_image)
            except tk.TclError:
                print("PhotoImage failed, skipping icon...")
        except Exception as e:
            print(f"Error setting icon: {e}")

    def set_format_and_style(self, format_type):
        self.format_var.set(format_type)
        if format_type == "mp3":
            self.mp3_button.config(bg="#4CAF50", fg="white")
            self.mp4_button.config(bg="#f0f0f0", fg="black")
        else:
            self.mp3_button.config(bg="#f0f0f0", fg="black")
            self.mp4_button.config(bg="#4CAF50", fg="white")
        self.update_options()

    def load_settings_into_ui(self):
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.config["download_path"])
        self.set_format_and_style(self.config["format"])
        if self.config["format"] == "mp4":
            self.quality_var.set(self.config["resolution"])
        else:
            self.quality_var.set(self.config["audio_bitrate"])

    def update_options(self):
        selected_format = self.format_var.get()
        if selected_format == "mp4":
            self.quality_menu["values"] = resolutions
            self.quality_var.set(self.config["resolution"])
        else:
            self.quality_menu["values"] = audio_bitrates
            self.quality_var.set(self.config["audio_bitrate"])

    def extract_video_id(self, url):
        pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/|youtube-nocookie\.com\/(?:watch\?v=))([\w-]{11})"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.config["download_path"] = path

    def add_tasks(self):
        urls = [entry.get().strip() for entry in self.url_entries]
        for url in urls:
            if url:
                video_id = self.extract_video_id(url)
                if not video_id:
                    messagebox.showerror("Invalid Link", f"Could not extract video ID from link: {url}")
                    continue
                standard_url = f"https://www.youtube.com/watch?v={video_id}"
                task_info = {
                    "url": standard_url,
                    "title": standard_url,
                    "format": self.format_var.get(),
                    "quality": self.quality_var.get(),
                    "path": self.path_entry.get()
                }
                self.download_queue.put(task_info)
                self.create_task_ui(task_info)
                self.start_next_download()

    def create_task_ui(self, task_info):
        """One-line display: [progress bar] [xx%] [filename]"""
        task_frame = tk.Frame(self.task_container, padx=5, pady=2, bg="#f9f9f9", bd=1, relief="solid")
        task_frame.pack(fill=tk.X, pady=1, padx=2)

        progress_bar = ttk.Progressbar(task_frame, orient="horizontal", length=75, mode="determinate")
        progress_bar.pack(side=tk.LEFT, padx=5)

        percent_label = tk.Label(task_frame, text="0%", width=5, anchor="w", bg="#f9f9f9")
        percent_label.pack(side=tk.LEFT)

        title_label = tk.Label(task_frame, text=task_info["title"], anchor="w", bg="#f9f9f9")
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        task_info["frame"] = task_frame
        task_info["progress_bar"] = progress_bar
        task_info["percent_label"] = percent_label
        task_info["title_label"] = title_label

    def start_next_download(self):
        if self.current_downloads < MAX_WORKERS and not self.download_queue.empty():
            task = self.download_queue.get()
            self.current_downloads += 1
            thread = threading.Thread(target=self.download_video, args=(task,))
            thread.start()
            self.download_threads.append(thread)

    def download_video(self, task):
        ydl_opts = {
            'outtmpl': os.path.join(task["path"], '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: self.update_progress(task, d)]
        }

        if task["format"] == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': task["quality"].replace("kbps", "")
                }]
            })
        else:
            ydl_opts.update({
                'format': f'bestvideo[height<={task["quality"].replace("p","")}]'+"/bestaudio",
                'merge_output_format': 'mp4'
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task["url"], download=True)
                title = info.get("title", task["url"])
                task["title_label"].config(text=title)
            task["percent_label"].config(text="100%")
            task["progress_bar"]["value"] = 100
        except Exception as e:
            task["percent_label"].config(text="Err")
            task["title_label"].config(text=f"Failed: {e}", fg="red")
        finally:
            self.current_downloads -= 1
            self.root.after(100, self.start_next_download)

    def update_progress(self, task, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if not total:
                return
            downloaded = d.get('downloaded_bytes', 0)
            percent = downloaded / total * 100
            task["progress_bar"]["value"] = percent
            task["percent_label"].config(text=f"{percent:.1f}%")
            self.root.update_idletasks()

    def export_config(self):
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
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError):
                return DEFAULT_CONFIG
        return DEFAULT_CONFIG


if __name__ == "__main__":
    root = tk.Tk()
    app = TubeMate(root)
    root.mainloop()
