from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
from pytubefix import YouTube
from pytubefix.cli import on_progress

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("YouTube Downloader")
root.geometry("650x200")

global url_var
url_var = StringVar()

global save_directory

def get_path():
    save_directory = filedialog.askdirectory(initialdir="c:/videos/")
    print(save_directory)
    save_path_entry.insert(END, save_directory)


def download_video():
    global save_directory
    save_folder = save_path_entry.get()
    status_label.configure(text="Download Started", text_color="green")
    try:
        yt_link = url_var.get()
        yt_object = YouTube(yt_link, on_progress_callback = on_progress)
        video = yt_object.streams.get_highest_resolution()
        #video = yt_object.filter(only_audio=True).first()
        video.download(output_path=save_folder)
        print("Download Complete")
        status_label.configure(text="Download Complete", text_color="green")
    except Exception as e:
        print(f"Invalid link {e}")
        status_label.configure(text=e, fg="red")

top_frame = ctk.CTkFrame(root, fg_color="transparent")
top_frame.pack(pady=20)

url_label = ctk.CTkLabel(top_frame, text="Youtube URL: ")
url_label.grid(row=0, column=0, padx=5, sticky=W)

url_entry = ctk.CTkEntry(top_frame, width = 420,
    height=30, corner_radius=5, textvariable=url_var)
url_entry.grid(row=0, column=1, columnspan=3, padx=10, sticky=E)

save_path_label = ctk.CTkLabel(top_frame, text="Choose Folder to Save Video: ")
save_path_label.grid(row=1, column=0, padx=5, pady=10, sticky=W)

save_path_entry = ctk.CTkEntry(top_frame, width = 350, height=30)
save_path_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky=W)

save_path_button = ctk.CTkButton(top_frame, width=60, text="Search", command=get_path)
save_path_button.grid(row=1, column=3, pady=5, sticky=W)

down_button = ctk.CTkButton(root, text="Download", command=download_video)
down_button.pack()

status_label = ctk.CTkLabel(root, text="Status: ",font=("Arial", 14), text_color="green")
status_label.pack(pady=10)


root.mainloop()
