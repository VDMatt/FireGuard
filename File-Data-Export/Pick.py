
#crea un array con tutti i file all'interno di una cartella
#per ognuno dei file, prendi il framerate
#se è a 16khz, non fare niente, altrimenti ricampiona (necessario backup del dataset)

import random
import os

dst="/Sort_Crick" #Copiare la cartella da processare nella directory dello script (Esempio: /Nomecartella)
src="/Split_Crick" #La cartella di destinazione verrà creata nella directory dello script


path = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(path+dst):
    os.makedirs(path+dst)

# Questo ciclo itera nella cartella dei slice e ne prende n a caso
folder = path+src
for i in range(0,20,1):
    randfile=random.choice(os.listdir(folder))
    os.replace(path+src+"/"+randfile, path+dst+"/"+randfile)

print("Done")
