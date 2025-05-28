from tkinter import *
import pygame
from tkinter import filedialog
from tkinter import messagebox
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = Tk()
root.title('Tonyplayer')
root.geometry("630x480")

# Initialise Pygame Mixer
pygame.mixer.init()

songs = []
current_song = ""

def play_time():
    if stopped:
        return

    # Grab Current Song Elapsed Time
    current_time = pygame.mixer.music.get_pos() / 1000
    # Convert to Time Format
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
    # Grab song title from playlist
    song = song_box.get(ACTIVE)
    song = os.path.join(root.directory + "/", song)
    # Load Song with Mutagen
    song_mut = MP3(song)
    # Get Song Length
    global song_length
    song_length = song_mut.info.length
    # Convert to time format
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
    # Increase Current Time By 1 second
    current_time += 1

    if int(my_slider.get()) == int(song_length):
        status_bar.config(text=f'Time Elaspsed = {converted_song_length}  of  {converted_song_length}  ')
    elif paused:
        pass
    elif int(my_slider.get()) == int(current_time):
        # Update Slider to position
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(current_time))
    else:
        # Update slider to position
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(my_slider.get()))
        # Convert to Time Format
        converted_current_time = time.strftime('%M:%S', time.gmtime(int(my_slider.get())))

        #Output Time To Status Bar
        status_bar.config(text=f'Time Elaspsed = {converted_current_time}  of  {converted_song_length}  ')

        # Move this thing along by 1 second
        next_time = int(my_slider.get()) + 1
        my_slider.config(value=next_time)
        # Update Time
        status_bar.after(1000, play_time)



def add_album():
    global current_song
    root.directory = filedialog.askdirectory(initialdir='/media/tony/Network2/Music')

    for song in os.listdir(root.directory):
        name, ext = os.path.splitext(song)
        if ext == '.mp3':
            songs.append(song)
    for song in songs:
        song_box.insert("end", song)

    song_box.selection_set(0)
    current_song = songs[song_box.curselection()[0]]

def play():
    try:
        global current_song
        global stopped
        stopped = False
        current_song = song_box.get(ACTIVE)
        pygame.mixer.music.load(os.path.join(root.directory + "/", current_song))
        pygame.mixer.music.play(loops=0)
        np_label.config(text=f'Now Playing: {current_song}')

    # Call the play_time Function to get song length
        play_time()

        # Update Slider To Position
        # slider_position = int(song_length)
        # my_slider.config(to=slider_position, value=0)

        # Get Current Volume
        current_volume = pygame.mixer.music.get_volume()
        # Times by 100 to make it easier to work with
        current_volume = current_volume * 100
        # Change Volume Meter Picture
        if int(current_volume) < 1:
            volume_meter.config(image=vol0)
        elif int(current_volume) > 0 and int(current_volume) < 25:
            volume_meter.config(image=vol1)
        elif int(current_volume) >= 25 and int(current_volume) < 50:
            volume_meter.config(image=vol2)
        elif int(current_volume) >= 50 and int(current_volume) < 75:
            volume_meter.config(image=vol3)
        elif int(current_volume) >= 75 and int(current_volume) <= 100:
            volume_meter.config(image=vol4)
    except:
        messagebox.showwarning("Tony Player", "You Must Add Songs From The\n\nOrganise Menu First")
        pass
# Stop Playing Current Song
global stopped
stopped = False
def stop():
    # Stop song from playing
    pygame.mixer.music.stop()
    song_box.select_clear(ACTIVE)

    # Set Stop Variable to true
    global stopped
    stopped = True


# Create Global Pause variable
global paused
paused = False

# Pause and unpause current song
def pause(is_paused):
    global paused
    paused = is_paused

    if paused:
        # Unpause
        pygame.mixer.music.unpause()
        paused = False
    else:
        # Pause
        pygame.mixer.music.pause()
        paused = True

# Play the next song in the playlist
def next_song():
    try:
        # Reset slider and status bar
        status_bar.config(text='')
        my_slider.config(value=0)
        # Get the current song tuple number
        next_one = song_box.curselection()
        # Add one to the current song number
        next_one = next_one[0]+1
        # Grab song title from playlist
        current_song = song_box.get(next_one)
        #current_song = song_box.get(ACTIVE)
        pygame.mixer.music.load(os.path.join(root.directory + "/", current_song))

        #pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        # Clear the active bar in playlist location
        song_box.selection_clear(0, END)
        # Activate new song bar
        song_box.activate(next_one)
        # Set active bar to next song
        song_box.select_set(next_one, last=None)
        np_label.config(text=f'Now Playing: {current_song}')
    except:
        messagebox.showwarning("Tony Player", "You Have Reached The End\n\nOf The Playlist")
        pass


def previous_song():
    try:
        # Reset slider and status bar
        status_bar.config(text='')
        my_slider.config(value=0)
        # Get the current song tuple number
        prev_one = song_box.curselection()
        # Add one to the current song number
        prev_one = prev_one[0]-1
        # Grab song title from playlist
        current_song = song_box.get(prev_one)
        #current_song = song_box.get(ACTIVE)
        pygame.mixer.music.load(os.path.join(root.directory + "/", current_song))

        #pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        # Clear the active bar in playlist location
        song_box.selection_clear(0, END)
        # Activate new song bar
        song_box.activate(prev_one)
        # Set active bar to next song
        song_box.select_set(prev_one, last=None)
        np_label.config(text=f'Now Playing: {current_song}')
    except:
        messagebox.showwarning("Tony Player", "You Have Reached The Start\n\nOf The Playlist")
        pass


# Create Slider Function
def slide(x):
    # slider_label.config(text=f'{int(my_slider.get())} of {int(song_length)}')
    current_song = song_box.get(ACTIVE)
    pygame.mixer.music.load(os.path.join(root.directory + "/", current_song))
    pygame.mixer.music.play(loops=0, start=int(my_slider.get()))

# Create Volume Function
def volume(x):
    pygame.mixer.music.set_volume(volume_slider.get())

    # Get Current Volume
    current_volume = pygame.mixer.music.get_volume()
    # Times by 100 to make it easier to work with
    current_volume = current_volume * 100
    # Change Volume Meter Picture
    if int(current_volume) < 1:
        volume_meter.config(image=vol0)
    elif int(current_volume) > 0 and int(current_volume) < 25:
        volume_meter.config(image=vol1)
    elif int(current_volume) >= 25 and int(current_volume) < 50:
        volume_meter.config(image=vol2)
    elif int(current_volume) >= 50 and int(current_volume) < 75:
        volume_meter.config(image=vol3)
    elif int(current_volume) >= 75 and int(current_volume) <= 100:
        volume_meter.config(image=vol4)

def about_popup():
    messagebox.showinfo("Tony Player", "Created by Tony Winfield\n\nVersion 1.0 16/09/2024")



# Create Master Frame
master_frame = Frame(root)
master_frame.pack(pady=20)

# Create a Playlist Box
song_box = Listbox(master_frame, bg="black", fg="white", width=60)
song_box.grid(row=0, column=0)

# Define Player Control Button Images
back_btn_img = PhotoImage(file=resource_path('images/back50.png'))
forward_btn_img = PhotoImage(file=resource_path('images/forward50.png'))
play_btn_img = PhotoImage(file=resource_path('images/play50.png'))
pause_btn_img = PhotoImage(file=resource_path('images/pause50.png'))
stop_btn_img = PhotoImage(file=resource_path('images/stop50.png'))

# Define Volume Control Images
global vol0
global vol1
global vol2
global vol3
global vol4
vol0 = PhotoImage(file=resource_path('images/volume0.png'))
vol1 = PhotoImage(file=resource_path('images/volume1.png'))
vol2 = PhotoImage(file=resource_path('images/volume2.png'))
vol3 = PhotoImage(file=resource_path('images/volume3.png'))
vol4 = PhotoImage(file=resource_path('images/volume4.png'))

# Create Player Control Frame
controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0, pady=20)

# Create Volume Meter
volume_meter = Label(master_frame, image=vol4)
volume_meter.grid(row=1, column=1, padx=10)

# Create Volume Label Frame
volume_frame = LabelFrame(master_frame, text="Volume")
volume_frame.grid(row=0, column=1, padx=30)

# Create Player Control Buttons
back_button = Button(controls_frame, image=back_btn_img, borderwidth=0, command=previous_song)
forward_button = Button(controls_frame, image=forward_btn_img, borderwidth=0, command=next_song)
play_button = Button(controls_frame, image=play_btn_img, borderwidth=0, command=play)
pause_button = Button(controls_frame, image=pause_btn_img, borderwidth=0, command=lambda: pause(paused))
stop_button = Button(controls_frame, image=stop_btn_img, borderwidth=0, command=stop)

back_button.grid(row=0, column=0, padx=10)
forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=2, padx=10)
pause_button.grid(row=0, column=3, padx=10)
stop_button.grid(row=0, column=4, padx=10)

# Create a menu
my_menu = Menu(root)
root.config(menu=my_menu)

organise_menu = Menu(my_menu, tearoff=False)
organise_menu.add_command(label='Select Folder', command=add_album)
my_menu.add_cascade(label='Organise', menu=organise_menu)

about_menu = Menu(my_menu, tearoff=False)
about_menu.add_command(label="About", command=about_popup)
my_menu.add_cascade(label='About', menu=about_menu)

# Add Status Bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

# Create Music Position Slider
my_slider = ttk.Scale(master_frame, from_=0, to=100, orient=HORIZONTAL, length=360, value=0, command=slide)
my_slider.grid(row=2, column=0, pady=10)

# Create Volume Slider
volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=VERTICAL, length=125, value=1, command=volume)
volume_slider.pack(pady=10)

# Now Playing Label
np_label = Label(root, text="Now Playing: ")
np_label.pack(pady=5)


root.mainloop()