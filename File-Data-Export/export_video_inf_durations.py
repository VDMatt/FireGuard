
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
    def __init__(self, timestamp, predicted, fscore, expected):

        self.timestamp   = timestamp
        self.type    = predicted
        self.expected = expected
        self.Fconf = fscore
        self.Nconf = float("{:.3f}".format(1 - fscore))

    def print(self):
            print("Expected: " + self.expected + "  Predicted: " + self.type +" "+ str(self.timestamp)+ " Fire score: " + str(self.Fconf) + " Noise score: " + str(self.Nconf))

def avg(array):

    avg = 0.0
    for i in range (0, len(array),1):
        avg+=array[i]
    if len(array)!= 0:
        avg  = float("{:.3f}".format((float(avg/len(array)))))
    return avg


frames = []
# test timestamp definition

frame = Frame(0,0,0,15,"Invalid")
frames.append(frame)
frame = Frame(0,16,2,15,"Noise") #birds
frames.append(frame)
frame = Frame(2,16,4,15,"LNT") #birds + LNT
frames.append(frame)
frame = Frame(4,16,6,15,"Noise") #crickets
frames.append(frame)
frame = Frame(6,16,8,15,"LNT") #crickets + LNT
frames.append(frame)
frame = Frame(8,16,10,15,"Noise") #rain
frames.append(frame)
frame = Frame(10,16,12,15,"Noise") #wind
frames.append(frame)
frame = Frame(12,16,14,15,"Noise") #birds
frames.append(frame)
frame = Frame(14,16,16,15,"LNT") #birds + LNT
frames.append(frame)
frame = Frame(16,16,18,15,"Noise") #insects
frames.append(frame)
frame = Frame(18,16,20,15,"LNT") #insects + LNT
frames.append(frame)
frame = Frame(20,16,22,15,"Noise") #rain
frames.append(frame)
frame = Frame(22,16,24,15,"Noise") #wind
frames.append(frame)
frame = Frame(24,16,26,15,"LNT") #Campfire
frames.append(frame)
frame = Frame(26,16,28,15,"MNT") #birds + MNT
frames.append(frame)
frame = Frame(28,16,30,15,"MNT") #birds + MNT
frames.append(frame)
frame = Frame(30,16,32,15,"Noise") #birds
frames.append(frame)
frame = Frame(32,16,34,15,"Noise") #insects
frames.append(frame)
frame = Frame(34,16,36,15,"LNT") #campfire
frames.append(frame)
frame = Frame(36,16,40,15,"Noise") #rain
frames.append(frame)
frame = Frame(40,16,44,15,"MNT") #insects + MNT
frames.append(frame)
frame = Frame(44,16,46,15,"Noise") #wind
frames.append(frame)
frame = Frame(46,16,48,15,"ENT") #birds + ENT
frames.append(frame)
frame = Frame(48,16,50,15,"ENT") #birds + ENT
frames.append(frame)
frame = Frame(50,16,54,15,"Noise") #rain
frames.append(frame)
frame = Frame(54,16,58,15,"ENT") #insects + ENT
frames.append(frame)
frame = Frame(58,16,59,59,"LNT") #Campfire
frames.append(frame)

#load test input from txt file and assign decision output (Fire, Noise, Uncertain) based on given threshold
def load_input(file, threshold_):

    frame_index=0

    input = open(file,"r")
    data = input.readlines()

    inferences = []

    for line in data:

        if line[0].isdigit():

            startmin = int(line[0:2])
            startsec = int(line[3:5])
            fscore =   float("{:.3f}".format(float(line[6:11])))

            if fscore > threshold_:
                pred = "F"
            if fscore < threshold_:
                pred = "N"
            if fscore == threshold_:
                pred = "D"

            start_   = datetime.time(0,startmin,startsec)
            if start_>frames[frame_index].end:
                    frame_index+=1

            expected = frames[frame_index].type

            inf     = Inference(start_, pred, fscore, expected)

            inferences.append(inf)

        else:
            continue

    input.close()
    return inferences

inference = load_input('video_test_inferences.txt', 0.823)
with open( 'video_inf_durations.csv', 'w+', encoding='UTF8') as f:
    writer = csv.writer(f)
    for count in range(1,len(inference),1):

        A = datetime.datetime.combine(datetime.date.today(), inference[count].timestamp)
        B = datetime.datetime.combine(datetime.date.today(), inference[count-1].timestamp)

        seconds = A-B
        seconds = seconds.total_seconds()
        line = [seconds]
        writer.writerow(line)
