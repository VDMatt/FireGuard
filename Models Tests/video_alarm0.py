
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

def find_worst_frames(file_, threshold, skip_indexes, printing):

    data = load_input(file_, threshold)

    curr_inf_index = 0

    temp = []
    worst_fire_inferences = []
    worst_noise_inferences = []
    worst_fire = []
    worst_noise = []
    min_fire_score = 1.0
    min_noise_score = 1.0

    worst_fire_frame_index = 0
    worst_noise_frame_index = 0

    for curr_frame, frame in enumerate(frames):
        #print("Frame " + frame.type + " starting " + str(frame.start) + " ending " + str(frame.end))
        cons_fire = 0
        if curr_frame in skip_indexes or frame.type == "Invalid":
            #print("Frame " + frame.type + " starting " + str(frame.start) + " ending " + str(frame.end)+ " was skipped, inferences in this frame:")
            while data[curr_inf_index].timestamp <= frame.end:
                #print(str(data[curr_inf_index].timestamp) + ' ' + data[curr_inf_index].expected)
                curr_inf_index +=1

        else:

            if frame.type == "ENT" or frame.type == "MNT" or frame.type == "LNT":
                #Load every inference made during current frame on temp list
                while data[curr_inf_index].timestamp <= frame.end and curr_inf_index < len(data)-1:
                    temp.append(data[curr_inf_index])
                    #print(str(data[curr_inf_index].timestamp) + ' ' + data[curr_inf_index].expected)
                    if curr_inf_index < len(data)-1:
                        curr_inf_index +=1
                #Calculate wrong predictions
                accuracy = 0
                wrong_predictions = 0

                for i in range(0, len(temp),1):
                    if temp[i].type != "F":
                        wrong_predictions+=1
                #Calculate accuracy
                accuracy = float("{:.3f}".format((len(temp) - wrong_predictions)/len(temp)))

                if accuracy < min_fire_score:
                    worst_fire_inferences.clear()
                    min_fire_score = accuracy
                    worst_fire_frame_index = curr_frame
                    worst_fire = (min_fire_score, worst_fire_frame_index)
                    for i in temp:
                        worst_fire_inferences.append(i)
            elif frame.type == "Noise":
                #Load every inference made during current frame on temp list
                while data[curr_inf_index].timestamp <= frame.end and curr_inf_index < len(data)-1:
                    temp.append(data[curr_inf_index])
                    #print(str(data[curr_inf_index].timestamp) + ' ' + data[curr_inf_index].expected)
                    if curr_inf_index < len(data)-1:
                        curr_inf_index +=1
                #Calculate wrong predictions
                accuracy = 0
                wrong_predictions = 0
                for i in range(0, len(temp),1):
                    if temp[i].type != "N":
                        wrong_predictions+=1
                #Calculate accuracy
                accuracy = float("{:.3f}".format((len(temp) - wrong_predictions)/len(temp)))
                if accuracy < min_noise_score:
                    worst_noise_inferences.clear()
                    min_noise_score = accuracy
                    worst_noise_frame_index = curr_frame
                    worst_noise = (min_noise_score, worst_noise_frame_index)
                    for i in temp:
                        worst_noise_inferences.append(i)

        temp.clear()

    if printing:
        print("\nWorst fire accuracy in frame " + str(worst_fire[1]) + " type " + frames[worst_fire[1]].type + " starting at " + str(frames[worst_fire[1]].start) + " accuracy " + str(worst_fire[0])+"\n")
        print("Frame output: ")
        for i in worst_fire_inferences:
            print(i.type, end = ' ')
        print('\n')
        print("Worst noise accuracy in frame " + str(worst_noise[1]) + " type " + frames[worst_noise[1]].type + " starting at " + str(frames[worst_noise[1]].start) + " accuracy " + str(worst_noise[0])+"\n")
        print("Frame output: ")
        for i in worst_noise_inferences:
            print(i.type, end = ' ')
        print('\n')

    return worst_fire, worst_noise, worst_fire_inferences, worst_noise_inferences


def find_best_consec_fire(file_):

    thresh = 0.6
    #minimum difference to look for between consecutive fires in the worst fire frame and consecutive fire in the worst noise frame
    minimum_consecutive_delta = 2
    best_thresh = 0

    best_minw = []
    best_maxw = []

    #frames skipped to be able to have a minimum_consecutive_delta, this skipped frames will cause fake positive alarms
    skip_indexes = [5,7,11,21]

    when_fire = 0
    when_noise = 0
    best_thresh = 0
    best_minw = 0
    best_maxw = 0
    best_min_cons_fire_while_fire = 0
    best_max_cons_fire_while_noise = 0
    max_cons_fire_while_noise = 0
    max_cons_fire_while_fire = 0
    cons_fire_while_fire = 0
    cons_fire_while_noise = 0
    min_cons_fire_while_fire = 0
    max_cons_fire_while_noise = 0
    min_low = 100

    while thresh < 1:

        print('Evaluating best cons_fire threshold:' + str(thresh))

        #look for worst frames for given threshold
        worst_fire, worst_noise, worst_fire_inferences, worst_noise_inferences = find_worst_frames(file_, thresh, skip_indexes, 0)

        #calculate consecutive fires for each frame

        for noise in worst_noise_inferences:

            if noise.type != "N":
                cons_fire_while_noise +=1

            if noise.type == "N":
                cons_fire_while_noise = 0

            if cons_fire_while_noise > max_cons_fire_while_noise:
                max_cons_fire_while_noise = cons_fire_while_noise
                when_noise = noise.timestamp

        for fire in worst_fire_inferences:

            if fire.type != "N":
                cons_fire_while_fire +=1

            if fire.type == "N":
                cons_fire_while_fire = 0

            if cons_fire_while_fire > min_cons_fire_while_fire:
                min_cons_fire_while_fire = cons_fire_while_fire
                when_fire = fire.timestamp

        #print(min_cons_fire_while_fire-max_cons_fire_while_noise)
        print(str(min_cons_fire_while_fire) + " " + str(max_cons_fire_while_noise))

        if min_cons_fire_while_fire-max_cons_fire_while_noise >= minimum_consecutive_delta:
            min_low = max_cons_fire_while_noise
            best_thresh = thresh
            best_minw = worst_fire_inferences
            best_maxw = worst_noise_inferences
            best_min_cons_fire_while_fire = min_cons_fire_while_fire
            best_max_cons_fire_while_noise = max_cons_fire_while_noise

        thresh += 0.001
        worst_fire_inferences.clear()
        worst_noise_inferences.clear()
        max_cons_fire_while_noise = 0
        min_cons_fire_while_fire = 0
        consec_fire_while_noise = 0
        consec_fire_while_fire = 0

    print("\nBest threshold found " + str(float("{:.3f}".format(best_thresh))) + " - Margin: " + str(best_min_cons_fire_while_fire - best_max_cons_fire_while_noise ))
    print('Max cons. fire while noise ' + str(best_max_cons_fire_while_noise) + ' at ' + str(when_noise))
    print('Min cons. fire while fire ' + str(best_min_cons_fire_while_fire) + ' at ' + str(when_fire))
    print('\nWorst Fire Window:')
    if best_minw:
        for i in best_minw:
            print(i.type, end = ' ')
    print('\nWorst Noise Window:')
    if best_maxw:
        for i in best_maxw:
            print(i.type , end = ' ')
    print('')

path = os.path.dirname(os.path.abspath(__file__))
os.system("chmod +rwx " + path)

file1 = path + "/video_test_inferences.txt"



print('\n-------------------------------------- ' + file1 + '-----------------------------')
#use the function below to see which are the worst frame to add to the skip_indexes array 
#worst_fire, worst_noise, worst_fire_inferences, worst_noise_inferences = find_worst_frames(file1, 0.8, skip_indexes, 1)

find_best_consec_fire(file1)
