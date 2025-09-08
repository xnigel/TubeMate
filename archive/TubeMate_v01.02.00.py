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
xxxx
"""
# ---
# Password protection feature
# 这是一个硬编码的简单密码，请务必修改为您自己的密码以增强安全性
PASSWORD = "nigel"

class TubeMate:
    def __init__(self, root):
        self.root = root
        ver = "01.02.00"
        yr = "2025.09.08"
        self.root.title('TubeMate' + " (v" + ver +")" + " - " + yr)
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
        for idx, url in enumerate(urls):
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
                    "path": self.path_entry.get(),
                    "entry_widget": self.url_entries[idx]  # 绑定对应输入框
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
                'format': f'bestvideo[height<={task["quality"].replace("p","")}]' + "/bestaudio",
                'merge_output_format': 'mp4'
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task["url"], download=True)
                title = info.get("title", task["url"])
                task["title_label"].config(text=title)

            task["percent_label"].config(text="100%")
            task["progress_bar"]["value"] = 100

            # ✅ 下载成功后清空对应输入框
            if "entry_widget" in task:
                task["entry_widget"].delete(0, tk.END)

        except Exception as e:
            task["percent_label"].config(text="Err")
            task["title_label"].config(text=f"Failed: {e}", fg="red")
            # ❌ 下载失败 → 不清空输入框，保留原始 URL

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
