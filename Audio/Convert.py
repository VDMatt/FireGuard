
import os
import ffmpeg

dst=input("Enter source folder name:")
os.system("cd .")
os.system('for i in '+dst+'/*''; do ffmpeg -i "$i" "${i%.*}C.wav"; done')

path = os.path.dirname(os.path.abspath(__file__))
folder = path+"/"+dst
directory = os.fsencode(folder)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    print(filename)
    if filename.endswith("C.wav"):
        continue
    else:
        os.remove(folder+"/"+filename)
        continue
