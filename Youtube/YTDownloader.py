#This script downloads audio (.wav) from a list of youtube videos links saved in Videos.txt (same folder as script)

# importing the module
from pytube import YouTube
from pytube.cli import on_progress #progress bar
import os

link_array = []

dst=input("Enter destination folder name:")
dst="/"+dst
path = os.path.dirname(os.path.abspath(__file__))
folder=path+dst
if not os.path.exists(folder):
    os.makedirs(folder)

source=input("Enter txt source file name:")
with open(source+".txt", 'r') as file:
    link_array = file.read().splitlines()

# link of the video to be downloaded
for x in range(len(link_array)):
    print(str(x+1) + "/" + str(len(link_array)) )
    try:
        yt = YouTube(link_array[x], on_progress_callback=on_progress)
        print("Downloading " + yt.streams[0].title)
    except:
        print("Connection Error") #to handle exception

    video = yt.streams.filter(only_audio=True).first()

    try:
        out_file = video.download(folder)
    except:
        print("Some Error!")

    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)

print('Task Completed!')
