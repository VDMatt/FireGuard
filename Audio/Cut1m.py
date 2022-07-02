

from pydub import AudioSegment
import math
import os
import random

src=input("Source folder name:")
dummy=src
src="/"+src

dirs=[]

total_samples=input("How many sample do you need?")
total_samples=int(total_samples)

slice_lenght=input("How many seconds per slice?")
slice_lenght=int(slice_lenght)


class SplitWavAudioMubin():

    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

path = os.path.dirname(os.path.abspath(__file__))
data_folder=path+src
dirs = os.listdir(data_folder)
tot_files=0

#counting total audio samples in all subfolder
for i in range(0,len(dirs),1):

    subfolder = data_folder+"/"+dirs[i]
    directory = os.fsencode(subfolder)
    tot_files = tot_files + len(os.listdir(directory))

#calculate how many samples to get from each Audio
from_each = math.ceil(total_samples/tot_files)
print("I will pick  " + str(from_each) + " samples from each audio")

#create random samples subfolder
rand_folder = data_folder + "/Rand" + dummy
if not os.path.exists(rand_folder):
    os.makedirs(rand_folder)
    print("Created folder" + rand_folder)

# Divide each audio in from_each frames, get random seconds (slice_lenght long) inside that frame
file_counter=1
#fetching audio files
for i in range(0,len(dirs),1):

    subfolder=data_folder+"/"+dirs[i]
    directory = os.fsencode(subfolder)
    dir_files = os.listdir(directory)

    for file in dir_files:

        print("Splitting file " + str(file_counter)+ " of " + str(tot_files))
        filename = os.fsdecode(file)

        if filename.endswith(".wav"):

            file_counter+=1
            split_wav = SplitWavAudioMubin(subfolder, filename)
            duration  = split_wav.get_duration()
            step      = math.floor(duration/from_each) #frame frame lenght
            index     = 0 #lower bound of current frame

            #dividing the audio in from_each frames, get 5 seconds randomly inside that frame
            for i in range(0, from_each, 1):

                split_fn = str(i) + '_' + split_wav.filename
                start    = random.randint(0,(step-slice_lenght)*1000)
                t1       = (step * index)* 1000 + start
                t2       = t1 + (slice_lenght * 1000)
                split_audio = split_wav.audio[t1:t2]
                split_audio.export(rand_folder+"/"+split_fn, format="wav")
                index+=1
            continue

        else:
            print("File ",filename,"is not a wav.\n")
            continue
