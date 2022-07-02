

from pydub import AudioSegment
import math
import os
import random
from distutils.dir_util import copy_tree

src=input("Source folder name:") #Copiare la cartella da processare nella directory dello script (Esempio: /Nomecartella)
dummy=src
src="/"+src
dirs=[]

sort="/Sorted_"+dummy #destinazione dei campioni presi a random

slice_duration=input("Slice duration: ")
slice_duration=int(slice_duration)

min_slice_duration=input("Min slice duration: ") #durata minima di uno slice
min_slice_duration=int(min_slice_duration)

random_samples=input("How many random samples to get: ")
random_samples=int(random_samples)

class SplitWavAudioMubin():

    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_split, to_split, split_filename, directory_):
        t1 = from_split * slice_duration * 1000
        t2 = to_split * slice_duration * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(directory_+"/"+str(int(slice_duration/60))+"m_"+dirs[i]+"/"+split_filename, format="wav")

    def multiple_split(self, directory_, split):
        total_splits = math.ceil(self.get_duration() / slice_duration)
        for i in range(0, total_splits, 1):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i+split, split_fn, directory_)
            if i == total_splits - split:
                print("Sample",self.filename,"splitted succesfully")

path = os.path.dirname(os.path.abspath(__file__))
dirs = os.listdir(path+src)

for i in range(0,len(dirs),1):

    folder=path+src+"/"+dirs[i]
    if not os.path.exists(folder+"/"+str(int(slice_duration/60))+"m_"+dirs[i]):
        os.makedirs(folder+"/"+str(int(slice_duration/60))+"m_"+dirs[i])
    directory = os.fsencode(folder)
    for file in os.listdir(directory):

        filename = os.fsdecode(file)

        if filename.endswith(".wav"):
            split_wav = SplitWavAudioMubin(folder, filename)
            split_wav.multiple_split(folder, split=1)
            continue
        else:
            print("File ",filename,"is not a wav.\n")
            continue

        duration=split_wav.get_duration()

        if duration<min_slice_duration*1000:
            os.remove(folder+"/"+filename)
            print(filename, "deleted because its duration was", duration, "seconds")
            continue

        print("Splitting in folder" + dirs[i] +" completed\nSorting..")
