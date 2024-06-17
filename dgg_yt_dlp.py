import re
import tkinter as tk
from tkinter import ttk
import subprocess
import sv_ttk
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os 

load_dotenv()  # take environment variables from .env.
time_str = datetime.now().strftime("%H%M%S")
yt_dlp = Path.cwd() / 'theme' / "yt-dlp.exe"

def extract_youtube_base_url(input_url):
    # Regex to match the main part of YouTube URLs (both short and long versions)
    regex = r"(https://(www\.)?youtube\.com/watch\?v=|https://youtu\.be/)([^&?/\s]+)"
    # Search for matches using the regex
    match = re.search(regex, input_url)
    # If a match is found, reconstruct the base YouTube URL
    if match:
        video_id = match.group(3)
        base_url_long = f"https://www.youtube.com/watch?v={video_id}"
        base_url_short = f"https://youtu.be/{video_id}"
        # Return both possibilities, or select one depending on your need
        return base_url_long, base_url_short
    return None

# def download_video():
#     youtube_url = url_entry.get()
#     if "&" in youtube_url:
#         youtube_url = youtube_url.split("&")[0]
#     start_time = start_time_entry.get()
#     end_time = end_time_entry.get()
#     filename = f"'{youtube_url.split('=')[-1]}_{time_str}.mp4'".strip(' ')
    
#     # Construct the command for yt-dlp
#     command = [
#         str(yt_dlp), youtube_url, "--downloader", "ffmpeg", "-N", '6', '--format', 'mp4',
#         "--downloader-args", f"ffmpeg_i:-ss {start_time} -to {end_time}" 
#     ]
#     print(str(command))
#     try:
#         # Attempt to download the video clip
#         subprocess.run(command, check=True)
#         message_label.config(text="Download Successful!", foreground="lime green")
#     except subprocess.CalledProcessError:
#         message_label.config(text="Download Failed! Check the details and try again.", foreground="red")


# try:
#     # Create the GUI app
#     root = tk.Tk()
#     theme = Path.cwd() / "azure.tcl"
#     root.tk.call("source", str(theme))
#     root.tk.call("set_theme", "dark")
# except Exception as e:
#     print('no theme file')

# root.title("DGG YouTube Partial Clip Downloader")
# # Use a frame to organize widgets
# main_frame = ttk.Frame(root)

# main_frame.pack(padx=10, pady=10, fill="both", expand=True)

# # URL Entry
# ttk.Label(main_frame, text="YouTube URL:").grid(column=0, row=0, sticky="w")
# url_entry = ttk.Entry(main_frame, width=50)
# url_entry.grid(column=1, row=0, sticky="ew", padx=5, pady=5)

# # Start Time Entry
# ttk.Label(main_frame, text="Start Time (in seconds):").grid(column=0, row=1, sticky="w")
# start_time_entry = ttk.Entry(main_frame, width=50)
# start_time_entry.grid(column=1, row=1, sticky="ew", padx=5, pady=5)

# # End Time Entry
# ttk.Label(main_frame, text="End Time (in seconds):").grid(column=0, row=2, sticky="w")
# end_time_entry = ttk.Entry(main_frame, width=50)
# end_time_entry.grid(column=1, row=2, sticky="ew", padx=5, pady=5)

# # Download Button
# download_button = ttk.Button(main_frame, text="Download Clip", command=download_video)
# download_button.grid(column=1, row=3, sticky="ew", padx=5, pady=10)

# # Message Label
# message_label = ttk.Label(main_frame, text="")
# message_label.grid(column=0, row=4, columnspan=2, sticky="ew")

# # Configure grid column
# main_frame.columnconfigure(1, weight=1)

# root.mainloop()

def find_words_in_captions(words, json_data):
    result = {word: [] for word in words}
    for video_id, content in json_data.items():
        for caption in content["captions"]:
            for word in words:
                if word in caption["text"]:
                    result[word].append({"videoID": video_id, "start": caption["start"]})
    return result

class PartialClipDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.clipboard_content = ""
        self.monitoring_clipboard = False
        self._apply_theme()
        self._create_widgets()
        self.start_clipboard_monitoring()
        
    def _apply_theme(self):
        """Apply the dark theme from an external file if available."""
        try:
            theme = Path.cwd() / "azure.tcl"
            self.root.tk.call("source", str(theme))
            self.root.tk.call("set_theme", "dark")
        except Exception as e:
            print('No theme file found. Using default theme.')

    def _create_widgets(self):
        """Create and layout the widgets in the main application window."""
        self.root.title("DGG YouTube Partial Clip Downloader")

        # Use a frame to organize widgets
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Configure the grid column to allow the Entry widgets to expand
        self.main_frame.columnconfigure(1, weight=1)

        # URL Entry
        ttk.Label(self.main_frame, text="YouTube URL:").grid(
            column=0, row=0, sticky="w")
        self.url_entry = ttk.Entry(self.main_frame, width=50, texvariable=os.environ.get('URL'))
        self.url_entry.grid(column=1, row=0, sticky="ew", padx=5, pady=5)

        # Start Time Entry
        ttk.Label(self.main_frame, text="Start Time (in seconds):").grid(
            column=0, row=1, sticky="w")
        self.start_time_entry = ttk.Entry(self.main_frame, width=50)
        self.start_time_entry.grid(
            column=1, row=1, sticky="ew", padx=5, pady=5)

        # End Time Entry
        ttk.Label(self.main_frame, text="End Time (in seconds):").grid(
            column=0, row=2, sticky="w")
        self.end_time_entry = ttk.Entry(self.main_frame, width=50)
        self.end_time_entry.grid(column=1, row=2, sticky="ew", padx=5, pady=5)
        # Download Button
        # This button will ideally trigger the download process for the video clip.
        # The 'command' parameter is expected to link to a method that handles the download.
        # Here you should replace 'self.download_video' with the actual method name once implemented.
        self.download_button = ttk.Button(
        self.main_frame, text="Download Clip", command=self.download_video)
        self.download_button.grid(
            column=1, row=3, sticky="ew", padx=5, pady=10)

        # Message Label
        # This label can be used to display messages to the user, such as download progress or errors.
        self.message_label = ttk.Label(self.main_frame, text="")
        self.message_label.grid(column=0, row=4, columnspan=2, sticky="ew")

    def _add_right_click_menu(self):
        """Adds right-click context menu with 'Paste' functionality to entry widgets."""
        self.rc_menu = tk.Menu(self.root, tearoff=0)
        self.rc_menu.add_command(label="Paste", command=self._paste)

        self.url_entry.bind("<Button-3>", self._show_rc_menu)
        self.start_time_entry.bind("<Button-3>", self._show_rc_menu)
        self.end_time_entry.bind("<Button-3>", self._show_rc_menu)

    def _show_rc_menu(self, event):
        """Shows right-click menu."""
        try:
            self.rc_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.rc_menu.grab_release()

    def _paste(self):
        """Pastes content from clipboard to focused widget."""
        try:
            self.root.focus_get().insert(tk.INSERT, self.root.clipboard_get())
        except tk.TclError:
            pass


    def extract_timestamp_from_url(self, url):
        if "t=" in url:
            timestamp = url.split("t=")[-1]
            if "s" in timestamp:
                timestamp = timestamp.replace("s", "")
            # Handling the case where there might be other parameters after 't'
            timestamp = timestamp.split("&")[0] if "&" in timestamp else timestamp
            return timestamp
        return ""


    def start_clipboard_monitoring(self):
        """Starts monitoring the clipboard in a non-blocking way."""
        if not self.monitoring_clipboard:
            self.monitoring_clipboard = True
            try:
                self.monitor_clipboard_for_youtube_url()
            except Exception as e:
                print(f"\n\nError monitoring clipboard: {e}\n\nthis is NOT an issue, just a warning.")


    def monitor_clipboard_for_youtube_url(self):
        """Monitors the clipboard for YouTube URLs and sets it in the URL entry if detected."""
        clipboard_content = self.root.clipboard_get()
        if "youtube.com" in clipboard_content and clipboard_content != self.clipboard_content:
            self.clipboard_content = clipboard_content
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_content)
            timestamp = self.extract_timestamp_from_url(clipboard_content)
            if timestamp:
                self.start_time_entry.delete(0, tk.END)
                self.start_time_entry.insert(0, timestamp)
                try:
                    timestamp = int(timestamp) + 60
                except Exception as e:
                    print(f'Error converting timestamp:{e}')
                self.end_time_entry.delete(0, tk.END)
                self.end_time_entry.insert(0, timestamp)
        self.root.after(1000, self.monitor_clipboard_for_youtube_url)

    def download_video(self):
        youtube_url = self.url_entry.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()
        
        if "&" in youtube_url:
            youtube_url = youtube_url.split("&")[0]
        # Ensure time string is in a proper format if added to the filename
        time_str = f"{start_time}-{end_time}"
        filename = f"{youtube_url.split('=')[-1]}_{time_str}.mp4".strip()

        # Path to the yt-dlp executable
        yt_dlp = Path.cwd() / "theme" / "yt-dlp"  # Assume yt-dlp is in PATH. Adjust if needed.

        # Construct the command for yt-dlp

        command = [
            str(yt_dlp), youtube_url, "--downloader", "ffmpeg", "-N", '6', '--format', 'mp4',
            "--downloader-args", f"ffmpeg_i:-ss {start_time} -to {end_time}"
        ]
        print(f"Executing command:{command}")
        try:
            # Attempt to download the video clip
            subprocess.run(command, check=True)
            self.message_label.config(
                text="Download Successful!", foreground="lime green")
        except subprocess.CalledProcessError:
            self.message_label.config(
                text="Download Failed! Check the details and try again.", foreground="red")


def main():
    """Main function to create the tkinter GUI application."""
    root = tk.Tk()
    
    app = PartialClipDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
