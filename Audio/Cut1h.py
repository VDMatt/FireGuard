
from pydub import AudioSegment
import math
import os
import random
print("\nThe scripts cuts 1h randomly from all files inside a folder" )
src=input("Source folder name:") #Copiare la cartella da processare nella directory dello script (Esempio: /Nomecartella)
dummy=src
src="/"+src
dst="/Cut"+dummy #La cartella di destinazione verrà creata nella directory dello script
slice_duration=3600 #(seconds in an hour)

path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(path+dst):
    os.makedirs(path+dst)

class SplitWavAudioMubin():

    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

# Questo ciclo itera nella cartella dei slice e li suddivide in slice da n secondi ognuno
folder = path+src
directory = os.fsencode(folder)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".wav"):
        print("Cutting " + filename)
        split_wav = SplitWavAudioMubin(folder, filename)
        duration=math.ceil(split_wav.get_duration())
        if duration>slice_duration:
            t1 = random.randint(0,(duration-slice_duration)*1000)
            t2 = t1 + (slice_duration * 1000)
            split_audio = split_wav.audio[t1:t2]
            split_audio = split_audio.set_channels(1)
            split_audio = split_audio.set_frame_rate(16000)
            split_audio.export(path + dst +"/"+split_wav.filename, format="wav")
            continue
        else:
            split_audio = AudioSegment.from_wav(split_wav.filepath)
            split_audio = split_audio.set_channels(1)
            split_audio = split_audio.set_frame_rate(16000)
            split_audio.export(path + dst +"/"+split_wav.filename, format="wav")
            continue
        continue
    else:
        print("File ",filename,"is not a wav.\n")
        continue

print("Splitting completed")
folder = path+src
directory = os.fsencode(folder)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    os.remove(folder+'/'+filename)
