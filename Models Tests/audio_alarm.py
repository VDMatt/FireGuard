
import sys
import os
import datetime
import queue
import math

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
    def __init__(self, start, end, type, confidence, expected):

        self.start   = start
        self.end     = end
        self.type    = type
        self.expected = expected

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
            print("Expected: " + self.expected + "  Predicted: " + self.type +" "+ str(self.start)+"-"+str(self.end) + " Fire score: " + str(self.Fconf) + " Noise score: " + str(self.Nconf))

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

#load test input from txt file
def load_input(file, threshold_):

    frame_index=0

    input = open(file,"r")
    data = input.readlines()

    inferences = []

    for line in data:

        if line[0].isdigit():

            startmin = int(line[0:2])
            startsec = int(line[3:5])
            endmin   = int(line[6:8])
            endsec   = int(line[9:11])
            pred     = line[11]

            score    = float("{:.3f}".format(float(line[13:18])))

            if pred == "N":
                nscore = score
                fscore = 1 - nscore
            elif pred == "F":
                fscore = score
                nscore = 1 - score
            elif pred == "D":
                fscore = 0.5
                nscore = 0.5

            if fscore > threshold_:
                pred = "F"
                score = fscore
            if fscore < threshold_:
                pred = "N"
                score = nscore
            if fscore == threshold_:
                pred = "D"
                score = 0

            start_   = datetime.time(0,startmin,startsec)
            end_    = datetime.time(0,endmin,endsec)
            expected = frames[frame_index].type

            if start_>=frames[frame_index].end:
                while start_>=frames[frame_index].start:
                    if start_<frames[frame_index].end or (end_<=frames[frame_index].end and start_>=frames[frame_index].start):
                        break
                    frame_index+=1

            if (start_<frames[frame_index].end and end_>frames[frame_index].end) or frames[frame_index].type=="Invalid":
                expected = "Invalid"
            inf     = Inference(start_, end_, pred, score, expected)
            # getting in which inference the frame belongs
            inferences.append(inf)

        else:
            continue

    input.close()
    return inferences

def check(file, window, thresh1, consecutive, thresh2, min_density):

    data = load_input(file, thresh1)

    consec_alarms = []
    dense_alarms = []
    history = []
    consec_fire = 0
    frame_ind = 0
    last_saved_ind = 0

    for count in range(0, len(data), 1):

        if data[count].start>frames[frame_ind].end:
            frame_ind +=1
            consec_fire = 0
            print("\n-----------------Frame " + str(frame_ind) + " type " + frames[frame_ind].type +  " starting at " + str(frames[frame_ind].start) + " ending at "  + str(frames[frame_ind].end) + "--------------------------\n\n")

        if consec_fire == consecutive:
            if last_saved_ind != frame_ind :
                tuple = (str(data[count].end), data[count].expected)
                consec_alarms.append(tuple)
                A = datetime.datetime.combine(datetime.date.today(), data[count].end)
                B = datetime.datetime.combine(datetime.date.today(), frames[frame_ind].start)
                delta = A - B
                print("Alarm launched at " + str(data[count].end) + " after " + str (delta) + " while " + data[count].expected + " was playing\n" )
                last_saved_ind = frame_ind
            consec_fire = 0

        if data[count].type == "F":
            consec_fire += 1
        if data[count].type != "F":
            consec_fire = 0

    for i in range (0,window, 1):
        history.append(data[i])


    density = 0
    frame_ind = 0
    last_saved_ind = 0
    data.clear()

    data = load_input(file, thresh2)

    print("\n------------------------ HISTORY FIRE DENSITY TEST --------------------------\n")

    for k in range(window, len(data)-1, 1):

        if data[k].start>frames[frame_ind].end:
            frame_ind +=1
            density = 0
            for i in range (0,len(history), 1):
                history.pop(0)
            print("\n-----------------Frame " + str(frame_ind) + " type " + frames[frame_ind].type +  " starting at " + str(frames[frame_ind].start) + " ending at "  + str(frames[frame_ind].end) + "--------------------------\n\n")

        for i in range(0,len(history),1):
            if history[i].type != "N":
                density+=1

        if density >= min_density:
            if last_saved_ind != frame_ind :
                tuple = (str(data[k].end), data[k].expected)
                dense_alarms.append(tuple)
                A = datetime.datetime.combine(datetime.date.today(), data[k].end)
                B = datetime.datetime.combine(datetime.date.today(), frames[frame_ind].start)
                delta = A - B
                print("Alarm launched at " + str(data[k].end) + " after" + str (delta) + " while " + data[k].expected + " was playing\n" )
                last_saved_ind = frame_ind
        if len(history) ==  window:
            history.pop(0)

        history.append(data[k])
        density = 0

    return consec_alarms, dense_alarms

path = os.path.dirname(os.path.abspath(__file__))
data_folder=path+"/model_inf/"
os.system("chmod +rwx " + data_folder)

file1 = data_folder + "1-MFE-CONV1D-2C.txt"
file2 = data_folder + "2-MFE-CONV2D-2C.txt"
file3 = data_folder + "3-SPECTRO-CONV1D-2C.txt"
file4 = data_folder + "4-MFE-CONV1D-4C.txt"
file5 = data_folder + "5-SPECTRO-CONV2D-4CV1.txt"
file6 = data_folder + "6-SPECTRO-CONV2D-4CV2.txt"

'''
MFE-CONV1D-2C

Best cons_fire threshold 0.808 - Margin: 2
Max cons. fire while noise 1 at 00:14:23
Min cons. fire while fire 3 at 00:28:56

Best fire_density threshold 0.69 - Margin: 7 - Score Margin: 0.554
Min fire density while playing fire 8/20 with an avg window fire score of 0.63
Max fire density while playing noise 1/20 with an avg window fire score of 0.076
'''
print("\n\n\n ********************************" + file1 + "**********************************")
cons_alarms, dense_alarms = check(file1, 20, 0.808, 3, 0.69, 8)

'''
MFE-CONV2D-2C:
Best cons_fire threshold: 0.909 - Margin: 4
Max cons. fire while noise 1 at 00:14:18
Min cons. fire while fire 5 at 00:55:45

Worst Fire Window:
N N F N N F N F N N N F F F N F F F F F N N N N N N N N N N F N F N N
Worst Noise Window:
N N N N F N N N N N N F N N F N F N N N N N N N N N N N N N N N N N N

Best fire_density threshold 0.89 - Margin: 9 - Score Margin: 0.499
Min fire density while playing fire 13/35 with an avg window fire score of 0.807
Max fire density while playing noise 4/35 with an avg window fire score of 0.308
'''
print("\n\n\n ********************************" + file2 + "**********************************")
#cons_alarms, dense_alarms = check(file2, 35, 0.909, 5, 0.89, 13)

'''
SPECTRO-CONV1D-2C:
Evaluating best cons_fire threshold: 0.897 - Margin: 2
Max cons. fire while noise 1 at 00:06:18
Min cons. fire while fire 3 at 00:08:15

Best fire_density threshold: 0.85 - Margin: 8 - Score Margin: 0.56
Min fire density while playing fire 9/35 with an avg window fire score of 0.633
Max fire density while playing noise 1/35 with an avg window fire score of 0.073

'''
print("\n\n\n ********************************" + file3 + "**********************************")
#cons_alarms, dense_alarms = check(file4, 35, 0.897, 3, 0.85, 9)

'''
MFE-CONV1D-4C:

Best cons_fire threshold: 0.917 - Margin: 2
Max cons. fire while noise 1 at 00:24:22
Min cons. fire while fire 3 at 00:58:26

Best fire_density threshold: 0.88 - Margin: 8 - Score Margin: 0.526
Min fire density while playing fire 9/25 with an avg window fire score of 0.595
Max fire density while playing noise 1/25 with an avg window fire score of 0.069
'''
print("\n\n\n ********************************" + file4 + "**********************************")
#cons_alarms, dense_alarms = check(file4, 25, 0.917, 3, 0.88, 9)

'''
SPECTRO-CONV2D-4CV1:

Best cons_fire threshold: 0.722 - Margin: 2
Max cons. fire while noise 1 at 00:06:19
Min cons. fire while fire 3 at 00:46:35

Best fire_density threshold: 0.65 - Margin: 12 - Score Margin: 0.373
Min fire density while playing fire 13/35 with an avg window fire score of 0.453
Max fire density while playing noise 1/35 with an avg window fire score of 0.08
'''
print("\n\n\n ********************************" + file5 + "**********************************")
#cons_alarms, dense_alarms = check(file5, 35, 0.722, 3, 0.65, 13)

'''
Best cons_fire threshold: 0.991 - Margin: 2
Max cons. fire while noise 1 at 00:24:17
Min cons. fire while fire 3 at 00:55:46

Best fire_density threshold: 0.73 - Margin: 9 - Score Margin: 0.333
Min fire density while playing fire 12/35 with an avg window fire score of 0.544
Max fire density while playing noise 3/35 with an avg window fire score of 0.211
'''
print("\n\n\n ********************************" + file6 + "**********************************")
#cons_alarms, dense_alarms = check(file6, 35, 0.991, 3, 0.73, 12)
