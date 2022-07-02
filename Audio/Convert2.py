from pydub import AudioSegment
import os
import subprocess
import math
import random

src=input("Enter source folder name:")
dummy=src
src="/"+src
dst="/Cut"+dummy #La cartella di destinazione verrà creata nella directory dello script
slice_duration=3600 #(seconds in an hour)


class SplitWavAudioMubin():

    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds


#Creating destination folder
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(path+dst):
    os.makedirs(path+dst)

path = os.path.dirname(os.path.abspath(__file__))
folder = path+src
directory = os.fsencode(folder)

for file in os.listdir(directory):

    filename = os.fsdecode(file)
    export = filename[:-4] + ".wav"
    print("Converting " + filename)
    subprocess.run(['ffmpeg', '-i', folder+"/"+filename, folder+"/"+export], check = True)
    os.remove(folder+'/'+filename)
    print("Cutting " + export)
    split_wav = SplitWavAudioMubin(folder, export)
    duration=math.ceil(split_wav.get_duration())

    if duration>slice_duration:
        t1 = random.randint(0,(duration-slice_duration)*1000)
        t2 = t1 + (slice_duration * 1000)
        split_audio = split_wav.audio[t1:t2]
        split_audio = split_audio.set_channels(1)
        split_audio = split_audio.set_frame_rate(16000)
        split_audio.export(path + dst +"/"+split_wav.filename, format="wav")
        print(export + " saved successfully, deleting old wav")
        os.remove(folder+'/'+export)
        continue
    else:
        split_audio = AudioSegment.from_wav(split_wav.filepath)
        split_audio = split_audio.set_channels(1)
        split_audio = split_audio.set_frame_rate(16000)
        split_audio.export(path + dst +"/"+split_wav.filename, format="wav")
        print(export + " saved successfully, deleting old wav")
        os.remove(folder+'/'+export)
        continue
