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
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bnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiCiAgICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOkdJTVA9Imh0dHA6Ly93d3cuZ2ltcC5vcmcveG1wLyIKICAgIHhtbG5zOmlwdGNFeHQ9Imh0dHA6Ly9pcHRjLm9yZy9zdGQvSXB0YzR4bXBFeHQvMjAwOC0wMi0yOS8iCiAgICB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgeG1wTU06RG9jdW1lbnRJRD0iZ2ltcDpkb2NpZDpnaW1wOjExM2U1NDkzLTkzNGUtNDY0My05MDA4LTY1NTUxNGU2NzkxNiIKICAgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo1OTBkNjI4ZC1iNGI3LTQ3YjgtODJkOC05ZWYyZWQzOTNiZmYiCiAgIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo1YWJiZWY2Zi05YWE5LTRjNTktYTc3Yi02NmEzYTFkMTUwNTAiCiAgIGRjOkZvcm1hdD0iaW1hZ2UvcG5nIgogICBleGlmOkRhdGVUaW1lT3JpZ2luYWw9IjIwMjUtMDktMDhUMDQ6MDU6MTkrMDA6MDAiCiAgIEdJTVA6QVBJPSIyLjAiCiAgIEdJTVA6UGxhdGZvcm09IldpbmRvd3MiCiAgIEdJTVA6VGltZVN0YW1wPSIxNzU3MzA0ODI2MTU3MzA4IgogICBHSU1QOlZlcnNpb249IjIuMTAuMzAiCiAgIGlwdGNFeHQ6RGlnaXRhbFNvdXJjZUZpbGVUeXBlPSJodHRwOi8vY3YuaXB0Yy5vcmcvbmV3c2NvZGVzL2RpZ2l0YWxzb3VyY2V0eXBlL2NvbXBvc2l0ZVdpdGhUcmFpbmVkQWxnb3JpdGhtaWNNZWRpYSIKICAgaXB0Y0V4dDpEaWdpdGFsU291cmNlVHlwZT0iaHR0cDovL2N2LmlwdGMub3JnL25ld3Njb2Rlcy9kaWdpdGFsc291cmNldHlwZS9jb21wb3NpdGVXaXRoVHJhaW5lZEFsZ29yaXRobWljTWVkaWEiCiAgIHBob3Rvc2hvcDpDcmVkaXQ9IkVkaXRlZCB3aXRoIEdvb2dsZSBBSSIKICAgcGhvdG9zaG9wOkRhdGVDcmVhdGVkPSIyMDI1LTA5LTA4VDA0OjA1OjE5KzAwOjAwIgogICB0aWZmOk9yaWVudGF0aW9uPSIxIgogICB4bXA6Q3JlYXRvclRvb2w9IkdJTVAgMi4xMCI+CiAgIDx4bXBNTTpIaXN0b3J5PgogICAgPHJkZjpTZXE+CiAgICAgPHJkZjpsaQogICAgICBzdEV2dDphY3Rpb249InNhdmVkIgogICAgICBzdEV2dDpjaGFuZ2VkPSIvIgogICAgICBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOmMwNDlhNjMwLWQ4ZTYtNDg4MC05YTYyLTNjNWJmM2Q4NTNmZiIKICAgICAgc3RFdnQ6c29mdHdhcmVBZ2VudD0iR2ltcCAyLjEwIChXaW5kb3dzKSIKICAgICAgc3RFdnQ6d2hlbj0iMjAyNS0wOS0wOFQxNDowOTowOSIvPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJzYXZlZCIKICAgICAgc3RFdnQ6Y2hhbmdlZD0iLyIKICAgICAgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpkYjUyODUxOC1iZDY5LTQ3NGUtOGRmNS0yMjVlZTc0ZjljMzAiCiAgICAgIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkdpbXAgMi4xMCAoV2luZG93cykiCiAgICAgIHN0RXZ0OndoZW49IjIwMjUtMDktMDhUMTQ6MTM6NDYiLz4KICAgIDwvcmRmOlNlcT4KICAgPC94bXBNTTpIaXN0b3J5PgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+RI+XWwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB+kJCAQNLltKcSoAABooSURBVHjatZt5jGTXdd5/595Xe1cvMz17z85ZuHNIiWMOJVIkJVlyYFKy5EQQKcrmIhlBEi0OFBmMBNhGFDgQlMQIoBiyBVqGCVswBUWRbJPiPsOdMyJn3zjT3dPdnJne966q9+7JH2+p96p6CASQe1CY6tf1Xp177lm+851z5fzmrQqgKAACaPg2dTX6EUElft/8P/68c47FIGDj/v2s2LKVX+fP5OAA52/fS9HksNZgxENSYiSCqjavxSLGAkrqPxEEgyfRIiW7zqY6NLtg0eyikx91qDoa6sIH/Jp/xJimEE4Qo0j0e3bTwhVJpBSB8DdJrVGaC/JiraXVo6QU0KbOlnVH96uCU/Ad/yI/6lI7azSyxFAJmb1I74yENixtm9VUghdqJ36IZtapONLmoRklhfoXiSxILAahZHUZ8/h1mEBqoU4QQ9YCEvGluQ4loyBJLkpipcu6QFNJqS+N7steSH2zKqjDV/2XcQEUE24/GMUZjaST8LpGwihtFhCL2jQSTVTnhX/Ult1dxgViO5Ks36koqKDqUFX8Fhl+bS6gikMBB2owziQbIslnJBsR039LbadIM3x6mvyiywjusr6e1mOsr9g0xQKQV0XUZQRvt+b/PwvRyPwES2j7BieKiTZIU8E5tgKNg7lKSwDLxghPWlJgdsXS/FtTzYm1pZ8nKEY1CajKlU1BVd9HCVmHjBWozkW7H1pBZPihkcaLVG2P1RIFwfRjNXZfwQNFVJNUkY4l7RkV4tCjLcpQVZwqjfhZGi90mdRxBcto0X7zc6qoavKdqEHC/W+auablzQbBrEbiGJVKgwqZxWs64rcIn924FDjQ0BWCSCOqinNB+zMk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
"""
# ---
# Password protection feature
# 这是一个硬编码的简单密码，请务必修改为您自己的密码以增强安全性
PASSWORD = "nigel"

class TubeMate:
    def __init__(self, root):
        self.root = root
        ver = "01.01.00"
        yr = "2025.09.08"
        self.root.title('TubeMate' + " (v" + ver +")" + " - " + yr + " - Nigel Zhai")
        self.root.geometry("500x500")
        self.root.minsize(500, 600)
        self.root.maxsize(500, 600)
        self.root.configure(bg="#f0f0f0")

        self.set_window_icon()

        self.download_queue = queue.Queue()
        self.download_threads = []
        self.current_downloads = 0

        self.config = self.load_config()

        self.setup_ui()
        self.load_settings_into_ui()

    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=5, pady=5, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame 1 - Settings
        settings_frame = tk.LabelFrame(main_frame, text="Settings", padx=5, pady=5, bg="#f0f0f0")
        settings_frame.pack(fill=tk.X, pady=5)

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
        url_frame = tk.LabelFrame(main_frame, text="Add Video Links", padx=5, pady=5, bg="#f0f0f0")
        url_frame.pack(fill=tk.X, pady=5)

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
        tasks_frame = tk.LabelFrame(main_frame, text="Download Tasks", padx=5, pady=5, bg="#f0f0f0")
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=5)
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

# ---
# 密码验证和主程序启动
def check_password():
    if password_entry.get() == PASSWORD:
        login_window.destroy()
        root.deiconify()  # Display window
        TubeMate(root)
    else:
        messagebox.showerror("Error!", "Incorrect password! Try again!")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide window

    login_window = tk.Toplevel(root)
    login_window.title("login")
    login_window.geometry("300x150")
    login_window.resizable(False, False)
    login_window.configure(bg="#f0f0f0")

    login_frame = tk.Frame(login_window, padx=20, pady=20, bg="#f0f0f0")
    login_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(login_frame, text="Enter password:", bg="#f0f0f0", font=("Arial", 10)).pack(pady=5)
    
    password_entry = tk.Entry(login_frame, show="*", width=20, font=("Arial", 10))
    password_entry.pack(pady=5)
    password_entry.bind("<Return>", lambda event=None: check_password())
    
    login_button = tk.Button(login_frame, text="Let me in", command=check_password, font=("Arial", 10))
    login_button.pack(pady=5)

    # 允许用户点击关闭按钮来退出程序
    login_window.protocol("WM_DELETE_WINDOW", login_window.destroy)
    
    # 因为主窗口是隐藏的，所以阻止对主窗口的关闭操作
    # 移除这行代码，因为在主程序显示后，我们需要允许关闭
    # root.protocol("WM_DELETE_WINDOW", lambda: None)
    
    root.mainloop()
