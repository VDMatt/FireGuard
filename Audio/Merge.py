
#crea un array con tutti i file all'interno di una cartella
#per ognuno dei file, prendi il framerate
#se è a 16khz, non fare niente, altrimenti ricampiona (necessario backup del dataset)
from pydub import AudioSegment
import os
import sys

try:
    directory_name=sys.argv[1]
    print(directory_name)
except:
    print('Please pass a directory')

src="/"+directory_name #Copiare la cartella da processare nella directory dello script (Esempio: /Nomecartella)
dummy=src[1:]
dest="Merged"+dummy
samples=[]


path = os.path.dirname(os.path.abspath(__file__))

folder = path+src
directory = os.fsencode(folder)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".wav"):
        print(path+src+"/"+filename)
        sample= AudioSegment.from_wav(path+src+"/"+filename)
        samples.append(sample)
        continue
    else:
        print("File ",filename,"is not a wav.\n")
        continue
merged=samples[0]
for i in range(0,len(samples),1):
    merged+=samples[i]
print(path+"/"+dest+".wav")
merged.export(path+"/"+dest+".wav", format="wav")
print("Exporting...")
print("Merging of samples completed!")
