

from pydub import AudioSegment
import math
import os
import random

src=input("Source folder name:") #Copiare la cartella da processare nella directory dello script (Esempio: /Nomecartella)
dummy=src
src="/"+src

dst="/Split_"+dummy #La cartella di destinazione verrà creata nella directory dello script
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

    def single_split(self, from_split, to_split, split_filename):
        t1 = from_split * slice_duration * 1000
        t2 = to_split * slice_duration * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(path + dst +"/"+split_filename, format="wav")

    def multiple_split(self, split):
        total_splits = math.ceil(self.get_duration() / slice_duration)
        for i in range(0, total_splits, 1):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i+split, split_fn)
            if i == total_splits - split:
                print("Sample",self.filename,"splitted succesfully")

path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(path+dst):
    os.makedirs(path+dst)


# Questo ciclo itera nella cartella dei slice e li suddivide in slice da n secondi ognuno
folder = path+src
directory = os.fsencode(folder)
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".wav"):
         split_wav = SplitWavAudioMubin(folder, filename)
         split_wav.multiple_split(split=1)
         continue
     else:
         print("File ",filename,"is not a wav.\n")
         continue
print("Splitting completed")

#Questo ciclo elimina i slice di durata minore di min_slice_duration
folder = path+dst
directory = os.fsencode(folder)
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".wav"):
         split_wav = SplitWavAudioMubin(folder, filename)
         duration=split_wav.get_duration()
         if duration<min_slice_duration:
             os.remove(folder+"/"+filename)
             print(filename, "removed because its duration was", duration, "seconds")
         continue
     else:
         print("File ",filename,"is not a wav.\n")
         continue

src=dst
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(path+sort):
    os.makedirs(path+sort)

# Questo ciclo itera nella cartella dei slice e ne prende n a caso
folder = path+src
for i in range(0,random_samples,1):
    randfile=random.choice(os.listdir(folder))
    os.replace(path+src+"/"+randfile, path+sort+"/"+randfile)

print("Sorting of",random_samples,"samples completed!")
