
import sys
import os
import datetime
import csv

class Frame:

    #hold start and end timestamp for each frame
    def __init__(self, startm, starts, endm, ends, type):

        self.start   = datetime.time(0,startm,starts)
        self.end     = datetime.time(0,endm,ends)
        self.type    = type

    def print(self):
        print("Sample type: " + self.type +" "+ str(self.start)+"-"+str(self.end))

class Inference:
    #hold start and end timestamp for each inference
    def __init__(self, startm, starts, endm, ends, type, confidence):

        self.start   = datetime.time(0,startm,starts)
        self.end     = datetime.time(0,endm,ends)
        self.type    = type

        if type == "F":
            self.Fconf = confidence
            self.Nconf = float("{:.3f}".format(1 - confidence))
        elif type == "N":
            self.Fconf = float("{:.3f}".format(1 - confidence))
            self.Nconf = confidence
        else:
            self.Fconf = 0
            self.Nconf = 0

    def print(self):
            print("Predicted: " + self.type +" "+ str(self.start)+"-"+str(self.end) + " Fire score: " + str(self.Fconf) + " Noise score: " + str(self.Nconf))

def avg(array):

    avg = 0.0
    for i in range (0, len(array),1):
        avg+=array[i]
    if len(array)!= 0:
        avg  = float("{:.3f}".format((float(avg/len(array)))))
    return avg


rexpected = []
# test timestamp definition

frame = Frame(0,0,0,15,"Invalid")
rexpected.append(frame)
frame = Frame(0,16,2,15,"Noise") #birds
rexpected.append(frame)
frame = Frame(2,16,4,15,"LNT") #birds + LNT
rexpected.append(frame)
frame = Frame(4,16,6,15,"Noise") #crickets
rexpected.append(frame)
frame = Frame(6,16,8,15,"LNT") #crickets + LNT
rexpected.append(frame)
frame = Frame(8,16,10,15,"Noise") #rain
rexpected.append(frame)
frame = Frame(10,16,12,15,"Noise") #wind
rexpected.append(frame)
frame = Frame(12,16,14,15,"Noise") #birds
rexpected.append(frame)
frame = Frame(14,16,16,15,"LNT") #birds + LNT
rexpected.append(frame)
frame = Frame(16,16,18,15,"Noise") #insects
rexpected.append(frame)
frame = Frame(18,16,20,15,"LNT") #insects + LNT
rexpected.append(frame)
frame = Frame(20,16,22,15,"Noise") #rain
rexpected.append(frame)
frame = Frame(22,16,24,15,"Noise") #wind
rexpected.append(frame)
frame = Frame(24,16,26,15,"LNT") #Campfire
rexpected.append(frame)
frame = Frame(26,16,28,15,"MNT") #birds + MNT
rexpected.append(frame)
frame = Frame(28,16,30,15,"MNT") #birds + MNT
rexpected.append(frame)
frame = Frame(30,16,32,15,"Noise") #birds
rexpected.append(frame)
frame = Frame(32,16,34,15,"Noise") #insects
rexpected.append(frame)
frame = Frame(34,16,36,15,"LNT") #campfire
rexpected.append(frame)
frame = Frame(36,16,40,15,"Noise") #rain
rexpected.append(frame)
frame = Frame(40,16,44,15,"MNT") #insects + MNT
rexpected.append(frame)
frame = Frame(44,16,46,15,"Noise") #wind
rexpected.append(frame)
frame = Frame(46,16,48,15,"ENT") #birds + ENT
rexpected.append(frame)
frame = Frame(48,16,50,15,"ENT") #birds + ENT
rexpected.append(frame)
frame = Frame(50,16,54,15,"Noise") #rain
rexpected.append(frame)
frame = Frame(54,16,58,15,"ENT") #insects + ENT
rexpected.append(frame)
frame = Frame(58,16,59,59,"LNT") #Campfire
rexpected.append(frame)

#load test input from txt file
def load_input(file, treshold, csvs):
    csvs = csvs[:-4]
    input = open(file,"r")
    data = input.readlines()
    frame_index = 0
    with open( csvs+'-mat.csv', 'w+', encoding='UTF8') as f:

        writer = csv.writer(f)
        line = ['start', 'end', 'score']
        writer.writerow(line)

        for line in data:

            if line[0].isdigit():

                startmin = int(line[0:2])
                startsec = int(line[3:5])
                endmin   = int(line[6:8])
                endsec   = int(line[9:11])
                pred     = line[11]

                score    = float("{:.3f}".format(float(line[13:18])))
                if pred != "F" and score<(1-treshold):
                    pred = "F"
                    score = float("{:.3f}".format(1-treshold))
                elif (pred == "N" and score==(1-treshold)):
                    pred  = "D"
                    score = 0
                inf      = Inference(startmin, startsec, endmin, endsec, pred, score)

                if inf.start>=rexpected[frame_index].end:
                    while inf.start>=rexpected[frame_index].start:
                        if inf.start<rexpected[frame_index].end or (inf.end<=rexpected[frame_index].end and inf.start>=rexpected[frame_index].start):
                            break
                        frame_index+=1

                writer = csv.writer(f)
                line = [str(inf.start), str(inf.end), str(inf.Fconf), rexpected[frame_index].type]
                writer.writerow(line)

            else:
                continue



path = os.path.dirname(os.path.abspath(__file__))
data_folder=path+"/model_inf"
os.system("chmod +rwx  " + data_folder)
enc_data_folder = os.fsencode(data_folder)
files = os.listdir(enc_data_folder)
for file in files:
    filename = os.fsdecode(file)
    os.system("chmod +rwx " + data_folder + "/" +filename)
    file = data_folder + "/" + filename
    load_input(file, 0.5, path+'/'+filename)
with open( path+'/frames.csv', 'w+', encoding='UTF8') as f:
    writer = csv.writer(f)
    line = ('start','end','type')
    writer.writerow(line)
    for i in range(0,len(rexpected),1):
        line = [rexpected[i].start, rexpected[i].end, rexpected[i].type]
        writer.writerow(line)
