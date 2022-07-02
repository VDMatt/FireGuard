
#crea un array con tutti i file all'interno di una cartella
#per ognuno dei file, prendi il framerate
#se è a 16khz, non fare niente, altrimenti ricampiona (necessario backup del dataset)
from pydub import AudioSegment
import math
import os

class SplitWavAudioMubin():

    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds


path = os.path.dirname(os.path.abspath(__file__))
folder = path+"/UnknownSample"
directory = os.fsencode(folder)

for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".wav"):
         split_wav = SplitWavAudioMubin(folder, filename)
         duration=split_wav.get_duration()
         if duration<5.0:
             os.remove(folder+"/"+filename)
             print(filename, "removed because duration was", duration)
         continue
     else:
         print("File ",filename,"is not a wav.\n")
         continue
