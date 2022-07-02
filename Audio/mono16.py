#This will convert all wav inside a given folder to mono file 16khz
from pydub import AudioSegment
import os

src=input("Enter source folder name:")
dummy=src
src="/"+src
print("Source is " + src)
dst="/mono16"+dummy #La cartella di destinazione verrà creata nella directory dello script
print("Dest is " + dst)

#Creating destination folder
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(path+dst):
    os.makedirs(path+dst)

path = os.path.dirname(os.path.abspath(__file__))
folder = path+src
directory = os.fsencode(folder)

for file in os.listdir(directory):

    filename = os.fsdecode(file)
    split_wav = AudioSegment.from_wav(folder + '/' + filename)
    split_wav = split_wav.set_channels(1)
    split_wav = split_wav.set_frame_rate(16000)
    print("Exporting to " + path + dst +"/"+filename)
    split_wav.export(path + dst +"/"+filename, format="wav")
