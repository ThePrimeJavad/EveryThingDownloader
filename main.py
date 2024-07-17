from tkinter import Tk, Canvas, Entry, Button, PhotoImage, filedialog, Label, StringVar, OptionMenu, ttk
import threading
from pathlib import Path
import yt_dlp
import os

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / path

def on_download_click():
    global stop_download_flag
    stop_download_flag = False
    download_message.set('')
    url = entry_1.get().strip()
    if not url:
        download_message.set("Please enter a valid URL.")
        return
    
    if 'playlist' in url:
        download_message.set('Playlist Found! Trying to Download...')
        threading.Thread(target=download_playlist, args=(url,)).start()
    elif 'www' in url:
        download_message.set('Trying to Download...')
        threading.Thread(target=download_video, args=(url,)).start()
    else:
        download_message.set("Unsupported URL format. Please check again.")

def download_video(url):
    global stop_download_flag
    try:
        format_choice = quality.get()
        ydl_opts = get_ydl_options(format_choice, single_video=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        download_message.set("Download Complete!")
    except StopDownloadException:
        download_message.set("Download Stopped.")
    except yt_dlp.utils.DownloadError as e:
        if 'This video is private' in str(e):
            download_message.set("Private video skipped.")
        else:
            print(f"Error: {e}")
            download_message.set("Error occurred during download.")
    except Exception as e:
        print(f"Error: {e}")
        download_message.set("Error occurred during download.")
    finally:
        stop_download_flag = True 

def download_playlist(url):
    global stop_download_flag
    try:
        format_choice = quality.get()
        ydl_opts = get_ydl_options(format_choice, single_video=False)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        download_message.set("Playlist download complete!")
    except StopDownloadException:
        download_message.set("Download Stopped.")
    except yt_dlp.utils.DownloadError as e:
        if 'private' in str(e):
            download_message.set("Private video skipped.")
        else:
            print(f"Error: {e}")
            download_message.set("Error occurred during playlist download.")
    except Exception as e:
        print(f"Error: {e}")
        download_message.set("Error occurred during playlist download.")
    finally:
        stop_download_flag = True 

def get_ydl_options(format_choice, single_video):
    global stop_download_flag
    outtmpl = f'{download_directory.get()}/%(title)s.%(ext)s' if single_video else f'{download_directory.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s'
    
    if format_choice == "audio only":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'noplaylist': single_video,
            'overwrites': False
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={format_choice.split("x")[1]}]+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': outtmpl,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'noplaylist': single_video,
            'overwrites': False
        }

    # Add the check for existing files
    ydl_opts['download_archive'] = str(OUTPUT_PATH / "downloaded.txt")

    return ydl_opts

def stop_download():
    global stop_download_flag
    stop_download_flag = True

def choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        download_directory.set(directory)
        download_message.set(f"Selected download directory: {download_directory.get()}")

class StopDownloadException(Exception):
    pass

def progress_hook(d):
    global stop_download_flag
    if stop_download_flag:
        raise StopDownloadException("Download stopped by user.")
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes')
        downloaded_bytes = d.get('downloaded_bytes')
        if total_bytes and downloaded_bytes:
            progress = downloaded_bytes / total_bytes * 100
            download_progress_bar['value'] = progress
            download_message.set(f"Downloading... {progress:.2f}% downloaded")
            window.update_idletasks()  # Force update of GUI
    elif d['status'] == 'finished':
        download_message.set("Download Complete!")

window = Tk()
window.geometry("856x541")
window.configure(bg="#FFFFFF")
download_directory = StringVar(value="Downloads")
download_message = StringVar(value="")
quality = StringVar(value="640x360")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=541,
    width=856,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

canvas.create_text(
    277.0,
    65.0,
    anchor="nw",
    text="1. Enter the URL:",
    fill="#000000",
    font=("Inter", 20 * -1)
)

canvas.create_text(
    277.0,
    166.0,
    anchor="nw",
    text="2. Choose The Quality:",
    fill="#000000",
    font=("Inter", 20 * -1)
)

canvas.create_text(
    277.0,
    266.0,
    anchor="nw",
    text="3. Choose The Save Location:",
    fill="#000000",
    font=("Inter", 20 * -1)
)

canvas.create_text(
    277.0,
    367.0,
    anchor="nw",
    text="4. Hit the Download Button:",
    fill="#000000",
    font=("Inter", 20 * -1)
)

button_1 = Button(
    text='Download',
    bg='#80B3FF',
    fg='#FFFFFF',
    font=('Arial', 12),
    borderwidth=0,
    highlightthickness=0,
    command=on_download_click,
    relief="flat"
)
button_1.place(
    x=441.0,
    y=407.0,
    width=96.0,
    height=44.0
)

button_2 = Button(
    text='Stop',
    bg='#FF6347',
    fg='#FFFFFF',
    font=('Arial', 12),
    borderwidth=0,
    highlightthickness=0,
    command=stop_download,
    relief="flat"
)
button_2.place(
    x=540.0,
    y=407.0,
    width=96.0,
    height=44.0
)

entry_image_1 = PhotoImage(
    file=str(relative_to_assets("entry_1.png")))
entry_bg_1 = canvas.create_image(
    534.5,
    124.0,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#80B3FF",
    fg="#ffffff",
    highlightthickness=0
)
entry_1.place(
    x=292.0,
    y=102.0,
    width=485.0,
    height=42.0
)

button_2 = Button(
    text='Choose...',
    bg='#80B3FF',
    fg='#FFFFFF',
    font=('Arial', 12),
    borderwidth=0,
    highlightthickness=0,
    command=choose_directory,
    relief="flat"
)
button_2.place(
    x=441.0,
    y=304.0,
    width=196.0,
    height=43.0
)

quality_options = ["256x144", "640x360", "854x480", "1280x720", "1920x1080", "audio only"]
dropdown_menu = OptionMenu(window, quality, *quality_options)
dropdown_menu.place(
    x=441.0,
    y=208.0,
    width=196.0,
    height=44.0,
)

label_message = Label(
    window,
    textvariable=download_message,
    bg="#FFFFFF",
    fg="#000000",
    font=("Inter", 16 * -1)
)
label_message.place(
    x=292.0,
    y=470.0,
    width=485.0,
    height=30.0
)

download_progress_bar = ttk.Progressbar(
    window,
    orient='horizontal',
    mode='determinate',
    length=485,
)
download_progress_bar.place(
    x=292.0,
    y=500.0,
)

canvas.create_text(
    32.0,
    500.0,
    anchor="nw",
    text="Made With 🧡 by Javad",
    fill="#000000",
    font=("Inter", 16 * -1)
)

canvas.create_text(
    35.0,
    56.0,
    anchor="nw",
    text="EveryThing",
    fill="#000000",
    font=('Arial', 25),
)
canvas.create_text(
    35.0,
    95.0,
    anchor="nw",
    text="Downloader",
    fill="#000000",
    font=('Arial', 25),
)

canvas.create_rectangle(
    468.0,
    311.0,
    495.0,
    340.0,
    fill="#FFFFFF",
    outline=""
)

canvas.create_rectangle(
    231.0,
    0,
    237.00000000000003,
    548.0,
    fill="#80B3FF",
    outline=""
)

image_image_1 = PhotoImage(
    file=str(relative_to_assets("image_1.png")))
image_1 = canvas.create_image(
    115.0,
    304.0,
    image=image_image_1
)

window.title("EveryThing Downloader")
window.resizable(False, False)
window.mainloop()
