#Title: Youtube Audio Player
#Author: Nathaniel Jackson
#Description: Pulls URLs from a text file and plays them at random.
#Version: 1.0
import os, vlc, pafy, random, datetime, math, threading, requests
from tkinter.constants import E, LEFT, NW, W
import tkinter as tk
from tkinter import messagebox, filedialog
from time import sleep
from PIL import ImageTk, Image
from io import BytesIO
import glob

# Things to look into
# Reading - File exist error

#Declaring global variables
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 400
FANCY_BACKGROUND = True

def main():
    """Initializes some variables and starts the GUI mainloop"""
    playlist = []
    song_data = []
    saved_urls = []
    player = vlc.MediaPlayer()
    forward = [True]
    create_main_GUI(playlist, song_data, saved_urls, player, forward)

def read_file():
    """Function reads the URL file from the same directory as
    Python script"""
    urls = []
    file = filedialog.askopenfile(defaultextension = '.txt', filetypes = (('Text File', ' *.txt'), ('All Files', '*.*')))

    while True:
        line = file.readline()

        #If line is empty, break
        if not line:
            break

        #Append line to list without \n
        urls.append(line.strip())
    file.close()

    return urls

def create_media(url):
    """Returns song object using pafy which has many methods useful for
    program (It contains all of the information about the video at the url)
    PARAM:
        url - url of youtube video"""
    song = pafy.new(url)

    return song

def get_best_quality(song):
    """Selects the best quality audio stream and returns it 
    this is data used to play the song
    PARAM:
        song - song object created from create_media()"""
    best_song = song.getbestaudio()
    best_song.bitrate
    '256'

    return best_song

def scramble_list(playlist, song_data, saved_urls, playlist_label):
    """Uses the zip and shuffle method to randomize the locations
    of the objects in playlist and song_data while making sure
    corresponding indexes remain the same
    PARAM:
        playlist - list of values generated by get_best_quality()
        song_data - list of values generated by create_media()
        saved_urls - list of urls in playlist
        playlist_label - label from tkinter that shows the current playlist"""
    temp_0 = list(zip(playlist, song_data, saved_urls))
    random.shuffle(temp_0)

    #clear data out to be appended
    playlist.clear()
    song_data.clear()
    saved_urls.clear()
    temp_1, temp_2, temp_3 = zip(*temp_0)
    playlist.extend(temp_1)
    song_data.extend(temp_2)
    saved_urls.extend(temp_3)
    display_playlist(playlist, playlist_label)   

def create_audio_list(urls, playlist, song_data):
    """Uses previous functions to create the lists
    playlist and song_data from a list of urls
    PARAM:
        urls - list of youtube urls
        playlist - list of values generated by get_best_quality()
        song_data - list of values generated by create_media() """
    for item in urls:
        song = create_media(item)
        song_data.append(song)
        song = get_best_quality(song)
        playlist.append(song)

def display_title_time(song, duration, player, title_label): 
    """Prints title of Video, time passed and time remaining.
    Param:
        song - song object currently playing from create_media() or song_data
        duration - total length of the song in seconds
        player - vlc object that plays the audio
        title_label - label that updates with the song and time"""
    #Check if video is paused
    while player.get_state() != vlc.State.Ended:
        if player.is_playing():
            time = player.get_time()
            time = math.ceil(time/1000)
            remaining = duration - time
            time_formatted = datetime.timedelta(seconds = time)
            remaining_formatted = datetime.timedelta(seconds = remaining)
            title_label.configure(text = f"{song.title}\n{time_formatted} / {remaining_formatted}")
            #duration -= 1
            sleep(1)
            if duration <= 0:
                break
        else:
            sleep(1)

def display_thumbnail(data, root, canvas):
    """Displays video thumbnail
    Param:
        data - song object from song_data
        root - tk main instance
        canvas - main window of tkinter GUI"""
    thumbnail_url = data.thumb
    response = requests.get(thumbnail_url)
    img_data = response.content
    root.thumbnail = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))

    canvas.create_image(CANVAS_WIDTH/4 - 60, CANVAS_HEIGHT/2 - 50, anchor = NW, image = root.thumbnail)

def display_playlist(playlist, playlist_label):
    """Displays the current playlist order
    Param:
        playlist - list of best audio variables
        playlist_label - tkinter label that displays the current playlist"""
    c = 1
    temp = ''
    for song in playlist:
        temp = temp + f'{c}: {song.title}\n'
        c += 1
    playlist_label.configure(text = temp, justify = LEFT)

def read_to_playlist(canvas, playlist, song_data, saved_urls, play_button, next_button, previous_button, playlist_label):
    """Used in the read_file_button on the GUI, uses other functions
    to read a text file and create  or add to playlist
    Param:
        canvas: canvas - main window of tkinter GUI
        playlist - list of best audio variables
        song_data - list of song variables
        play_button - tkinter play button
        next_button - ''
        previous button - ''
        playlist_label - tkinter label that displays the current playlist"""
    urls = read_file()
    create_audio_list(urls, playlist, song_data)
    display_playlist(playlist, playlist_label)
    saved_urls.extend(urls)
    
    place_buttons(canvas, play_button, next_button, previous_button)

def add_to_playlist(canvas, playlist, song_data, saved_urls, url, play_button, next_button, previous_button, playlist_label):
    """Adds song from URL field to playlist
    Param:
        canvas: canvas - main window of tkinter GUI
        playlist - list of best audio variables
        song_data - list of song variables
        url - youtube URL
        play_button - tkinter play button
        next_button - ''
        previous button - ''
        playlist_label - tkinter label that displays the current playlist"""
    saved_urls.append(url)
    song = create_media(url)
    song_data.append(song)
    song = get_best_quality(song)
    playlist.append(song)
    
    display_playlist(playlist, playlist_label)
    place_buttons(canvas, play_button, next_button, previous_button)

def clear_playlist(playlist, song_data, saved_urls, playlist_label):
    """Erases the current playlist, only safe during setup of playlist, not while listening
    Param:
        playlist - list of best audio variables
        song_data - list of song variables
        playlist_label - tkinter label that displays the current playlist"""
    playlist.clear()
    song_data.clear()
    saved_urls.clear()
    display_playlist(playlist, playlist_label)

def place_buttons(canvas, play_button, next_button, previous_button):
    """Places the buttons after a file is read or url 
    Param:
        canvas: canvas - main window of tkinter GUI
        play_button - tkinter play button
        next_button - ''
        previous button - '' """

    canvas.create_window(CANVAS_WIDTH/4, CANVAS_HEIGHT/2 + 80, window = play_button)
    canvas.create_window(CANVAS_WIDTH/4 + 50, CANVAS_HEIGHT/2 + 80, window = next_button)
    canvas.create_window(CANVAS_WIDTH/4 - 50, CANVAS_HEIGHT/2 + 80, window = previous_button)

def swap_play_button(player, play_button, playing):
    """Changes the play button to pause while the song is playing and back if it is paused
    PARAM:
        player -  vlc MediaPlayer object
        play_button - tkinter play button
        playing - Bool value true if song is playing"""
    if playing:
        play_button.configure(text = '⏸', foreground = '#ff1638', command = lambda: pause(player, play_button))
    else:
        play_button.configure(text = '▶', foreground = '#0c0', command = lambda: play(player, play_button))

def play_audio(root, canvas, song, data, player, title_label):
    """Plays audio. This is the function
    that actually runs vlc to play a song
    Param:
        root - tkinter main
        canvas - main tkinter window
        song - a pafy audio object, like those in playlist
        data - a pafy media file from song_data, holds information about song
        player - vlc MediaPlayer object, plays the song
        title_label - tkinter label, used to display current playing song."""
    #player = vlc.MediaPlayer()
    temp_media = vlc.Media(song.url)
    player.set_media(temp_media)
    player.play()

    sleep(2)
    
    #get_length returns time in milliseconds
    duration_ms = player.get_length()
    duration_s = math.ceil(duration_ms/1000)

    display_thumbnail(data, root, canvas)
    display_title_time(song, duration_s, player, title_label)
    return player

def play_audio_list(root, canvas, playlist, song_data, player, play_button, title_label, forward):
    """Plays a list of pafy audio objects.
    Param: 
        root - main tk object
        canvas - main window of tkinter GUI
        playlist - list of best audio variables
        song_data - list of song variables
        player - vlc mediaplayer object 
        play_button - tkinter play button
        title_label - tkinter label, displays current video title
        forward - bool list, tells the player to keep moving forward or to jump back"""
    swap_play_button(player, play_button, True)
    i = 0
    
    while i <= (len(playlist) - 1):
        play_audio(root, canvas, playlist[i], song_data[i], player, title_label)
        if forward[0]:
            i += 1 
        else:
            i -= 1    
            forward.clear()
            forward.append(True)
            
def play(player, play_button):
    """Function that plays with play_button, continues the vlc_player 
    when it has been paused
    PARAM:
        player - vlc MediaPlayer object
        play_button - tkinter button"""
    player.set_pause(0)
    swap_play_button(player, play_button, True)

def pause(player, play_button):
    """Function that pauses with play_button, cpauses the vlc_player 
    when it is playing
    PARAM:
        player - vlc MediaPlayer object
        play_button - tkinter button"""
    player.set_pause(1)
    swap_play_button(player, play_button, False)

def next_song(player):
    """Skips to the next song
    PARAM:
        player - vlc mediaplayer object"""
    
    player.set_position(0.999)

def previous_song(player, forward):
    """If the song is 3 seconds in this function moves the mediaplayer to previous song,
    otherwise it restarts the song
    PARAM:
        player - vlc mediaplayer object
        forward - boolean list tracking if the previous button has been selected to move
                  index"""
    if player.get_time() < 3000:
        forward.clear()
        forward.append(False)
        player.set_position(0.999)
    else: 
        player.set_position(0)

def set_volume(player, volume):
    """Takes input from the slider on the main window and adjusts player volume
    PARAM:
        player - vlc mediaplayer object
        volume - value from the slider 0-100"""
    player.audio_set_volume(volume)

def start_player_thread(root, canvas, playlist, song_data, player, play_button, title_label, forward):
    """Starts a thread for the player to begin. This prevents it from freezing the main tk window
    PARAM:
        root - main tk object
        canvas - main window of tkinter GUI
        playlist - list of best audio variables
        song_data - list of song variables
        player - vlc mediaplayer object 
        play_button - tkinter play button
        title_label - tkinter label, displays current video title
        forward - bool list, tells the player to keep moving forward or to jump back"""
    player_thread = threading.Thread(target = lambda: play_audio_list(root, canvas, playlist,
                             song_data, player, play_button, title_label, forward), daemon = True)
    player_thread.start()

def start_download_thread(best_song):
    """Starts download in another thread, so that tkinter doesn't freeze during download
    PARAM:
        best_song - best audio variable from pafy"""
    download_thread = threading.Thread(target = lambda: download_song(best_song), daemon = True)
    download_thread.start()

def start_download_list_thread(playlist):
    """Starts downloading the list in a seperate thread to not freeze tkinter window
    PARAM:
        playlist - list of best audio variables"""
    download_list_thread = threading.Thread(target = lambda: download_from_playlist(playlist), daemon = True)
    download_list_thread.start()

def download_song(best_song):
    """Downloads song in Music Download directory
    PARAM:
        best_song - best audio variable"""
    os.makedirs('Music Download', exist_ok = True)
    best_song.download('Music Download/')
    
def download_from_url(url):
    """Takes the url from the entry box and downloads the audio
    PARAM:
        url - youtube url"""
    song = create_media(url)
    best_song = get_best_quality(song)
    start_download_thread(best_song)

def download_from_playlist(playlist):
    """downloads all songs in the current playlist
    PARAM:
        playlist - list of best audio files"""
    original_location = os.getcwd()
    for song in playlist:
        download_song(song)
        downloading = True
        sleep(0.1)

        #This portion checks if the file is done downloading before moving onto the next song
        while downloading:
            os.chdir(original_location)
            os.chdir('Music Download')
            title = song.title

            #Titles can contain characters that files can't
            #Downloading replaces them with _'s 
            title = title.replace(':', '_')
            title = title.replace('/', '_')
            title = title.replace('\\', '_')
            title = title.replace('*', '_')
            title = title.replace('?', '_')
            title = title.replace('<', '_')
            title = title.replace('>', '_')
            title = title.replace('|', '_')

            if glob.glob(title + '.*'):
                downloading = False

        os.chdir(original_location)

def save_playlist(saved_urls):
    """This function saves the current playlist urls in a text file in the current directoru (not Music Download)
    PARAM:
        saved_urls - list of urls in playlist"""
    #file_name = simpledialog.askstring(title = 'File Name', prompt = 'Save as:', initialvalue = 'songs.txt')
    file = filedialog.asksaveasfile(defaultextension = '.txt', filetypes = (('Text File', ' *.txt'), ('All Files', '*.*')))

    #file = open(file_name, 'w')
    for url in saved_urls:
        file.write(url)
        file.write('\n')

    file.close()

def create_main_GUI(playlist, song_data, saved_urls, player, forward):
    """Creates tkinter canvas, buttons and labels
    Param: 
        playlist - list of best audio songs
        song_data - list of song pafy files (contain information)
        saved_urls - list of youtube urls for saving
        player - vlc mediaplayer object
        forward - list with bool variable"""

    root = tk.Tk()
    root.title("Youtube Audio Player")
    
    #Create and display canvas
    canvas = tk.Canvas(root, width = CANVAS_WIDTH, height = CANVAS_HEIGHT)
    canvas.pack()

    #Create entry for URL
    entry_url = tk.Entry(root)
    entry_url.insert(0,"<Enter a URL here>")

    url_label = tk.Label(root, text = "URL:")
    playlist_title = tk.Label(root, text = 'Playlist:')
    title_label = tk.Label(root, text = '')
    playlist_label = tk.Label(root, text = '')
    volume_label = tk.Label(root, text = 'Volume:')

    #Creating buttons
    play_button = tk.Button(root, text = "▶", foreground = '#0c0', command = lambda : start_player_thread(root, canvas, playlist,
                                 song_data, player, play_button, title_label, forward))
    read_file_button = tk.Button(root, text = "Load List", command = lambda : read_to_playlist(canvas,playlist, song_data, saved_urls, 
                                play_button, next_button, previous_button, playlist_label))
    random_button = tk.Button(root, text = "Shuffle", command = lambda: scramble_list(playlist, song_data, saved_urls, playlist_label))
    url_add_button = tk.Button(root, text = "Add", command = lambda: add_to_playlist(canvas, playlist, song_data, saved_urls,
                                 entry_url.get(), play_button, next_button, previous_button, playlist_label))
    next_button = tk.Button(root, text = "⏭", command = lambda : next_song(player))
    previous_button = tk.Button(root, text = "⏮", command = lambda : previous_song(player, forward))
    clear_button = tk.Button(root, text = "Clear", background = '#6a1638', foreground = '#fff', command = lambda : clear_playlist(playlist, song_data, saved_urls, playlist_label))
    url_down_button = tk.Button(root, text = "Download Song", command = lambda : download_from_url(entry_url.get()))
    playlist_down_button = tk.Button(root, text = "Download List", command = lambda : start_download_list_thread(playlist))
    save_button = tk.Button(root, text = "Save", background = '#0a0', foreground = '#fff', command = lambda : save_playlist(saved_urls))

    volume_slider = tk.Scale(root, from_= 0, to = 100, orient = 'horizontal')
    volume_slider.set(50)
    volume_slider.bind('<ButtonRelease>', lambda _: set_volume(player, volume_slider.get()))

    #Configures the GUI to have a special theme
    if FANCY_BACKGROUND:
        if glob.glob('GUI Design.png'):
            root.background_image = ImageTk.PhotoImage(file = 'GUI Design.png')
            canvas.create_image(0,0, image = root.background_image, anchor = NW)

            url_label.configure(background = '#ddd')
            playlist_title.configure(background = '#ddd')
            title_label.configure(background = '#100454', foreground = '#fff')
            playlist_label.configure(background = '#ddd')
            volume_label.configure(background = '#ddd')

            play_button.configure(background = '#100454', foreground = '#0c0')
            read_file_button.configure(background = '#100454', foreground = '#ffe100')
            random_button.configure(background = '#100454', foreground = '#ffe100')
            url_add_button.configure(background = '#100454', foreground = '#ffe100')
            next_button.configure(background = '#100454', foreground = '#ffe100')
            previous_button.configure(background = '#100454', foreground = '#ffe100')
            clear_button.configure(background = '#6a1638', foreground = '#fff')
            url_down_button.configure(background = '#100454', foreground = '#ffe100')
            playlist_down_button.configure(background = '#100454', foreground = '#ffe100')
            save_button.configure(background = '#0a0', foreground = '#fff')

            volume_slider.configure(background = '#ddd')
        
        else:
            messagebox.showinfo('Error', '\'GUI Design.png\' not found, resuming without fancy background')

    #Place entries and labels
    canvas.create_window(40, 15, anchor = W, window = entry_url)
    canvas.create_window(35, 15, anchor = E, window = url_label)
    canvas.create_window(CANVAS_WIDTH/2 + 100, 15, anchor = E, window = playlist_title)
    canvas.create_window(CANVAS_WIDTH/4, CANVAS_HEIGHT/2 + 50, window = title_label)
    canvas.create_window(CANVAS_WIDTH/2 + 53, 35, anchor = NW, window = playlist_label)

    #Place buttons
    canvas.create_window(5, 42, anchor = W, window = read_file_button)
    canvas.create_window(170, 15, anchor = W, window = url_add_button)
    canvas.create_window(215, 15, anchor = W, window = url_down_button)
    canvas.create_window(CANVAS_WIDTH/2 + 125, 15, window = random_button)
    canvas.create_window(CANVAS_WIDTH - 30, 15, window = clear_button)
    canvas.create_window(CANVAS_WIDTH/2 + 205, 15, window = playlist_down_button)
    canvas.create_window(CANVAS_WIDTH - 75, 15, window = save_button)
    canvas.create_window(CANVAS_WIDTH/2 - 150, CANVAS_HEIGHT - 20, window = volume_slider)
    canvas.create_window(CANVAS_WIDTH/2 - 225, CANVAS_HEIGHT - 10, window = volume_label)
    
    root.mainloop()

if __name__ == "__main__":
    main()
