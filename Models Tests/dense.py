
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

def fire_density(data, window, skip, skip2):

    fire_inf = []
    noise_inf = []

    for inf in data :

        if inf.expected == "ENT" or inf.expected == "MNT" or inf.expected == "LNT":
            fire_inf.append(inf)

        elif inf.expected == "Noise":
            noise_inf.append(inf)


    last_index = window - 1
    temp = []
    max_window = []
    min_window = []
    density = 0
    min_density_while_fire = window
    avg_score = 0
    timestamp = 0
    curr_frame = 0

    if skip[0] != 99:
        for k in range(0, len(fire_inf),1):
            for i in range(0,len(skip),1):
                if k<len(fire_inf):
                    if fire_inf[k].start>frames[skip[i]].start and fire_inf[k].end<frames[skip[i]].end:
                        while fire_inf[k].start<frames[skip[i]].end:
                            fire_inf.pop(k);

    #pre-load fire density array
    for i in range (0, window, 1):
        temp.append(fire_inf[i])

    while last_index <= len(fire_inf) - window - 1:
        '''
        if skip[0] < len(frames):
            for i in range(0,len(skip),1):
                if fire_inf[last_index].start>frames[skip[i]].start and fire_inf[last_index].start<frames[skip[i]].end:
                    while fire_inf[last_index].start<frames[skip[i]].end:
                        last_index+=1
        '''
        if fire_inf[last_index].start > frames[curr_frame].end:
            while fire_inf[last_index].start > frames[curr_frame].end:
                    curr_frame += 1
            temp.clear()
            for i in range (0, window, 1):
                    temp.append(fire_inf[last_index])
                    last_index += 1

        for i in range(0,len(temp),1):
            if temp[i].type != "N":
                density+=1


        if density < min_density_while_fire:
            avg_score = 0
            min_window.clear()
            min_density_while_fire = density
            timestamp = fire_inf[last_index].end
            for i in range(0,len(temp),1):
                avg_score += temp[i].Fconf
                min_window.append(temp[i])
            avg_score = float("{:.3f}".format(avg_score/window))

        temp.pop(0)
        if not last_index == len(fire_inf)-1:
            last_index +=1
        if not last_index > len(fire_inf)-1:
            temp.append(fire_inf[last_index])
        density = 0

    min = (min_density_while_fire, timestamp, avg_score)

    temp.clear()
    last_index = window - 1
    density = 0
    max_density_while_noise = 0
    curr_frame = 0

    for i in range (0,window, 1):
        temp.append(noise_inf[i])

    if skip2[0] != 99:
        for k in range(0, len(noise_inf),1):
            for i in range(0,len(skip2),1):
                if k < len(noise_inf):
                    if noise_inf[k].start>frames[skip2[i]].start and noise_inf[k].end<frames[skip2[i]].end:
                        while noise_inf[k].start<frames[skip2[i]].end:
                            noise_inf.pop(k);

    while last_index <= len(noise_inf) - window - 1:

        if noise_inf[last_index].start > frames[curr_frame].end:
            while noise_inf[last_index].start > frames[curr_frame].end:
                    curr_frame += 1
            temp.clear()
            for i in range (0, window, 1):
                    temp.append(noise_inf[last_index])
                    last_index += 1

        for i in range(0,len(temp),1):
            if temp[i].type != "N":
                density+=1

        if density > max_density_while_noise:
            avg_score = 0
            max_window.clear()
            max_density_while_noise = density
            timestamp = noise_inf[last_index].end
            for i in range(0,len(temp),1):
                avg_score += temp[i].Fconf
                max_window.append(temp[i])
            avg_score = float("{:.3f}".format(avg_score/window))


        temp.pop(0)
        if not last_index == len(noise_inf)-1:
            last_index +=1
        if not last_index > len(noise_inf)-1:
            temp.append(noise_inf[last_index])
        density = 0


    max = (max_density_while_noise, timestamp, avg_score)
    return min, max, min_window, max_window



def get_model_info(file):

    input = open(file,"r")
    data = input.readlines()
    if not (data[0][0].isdigit() or data[1][0].isdigit() or data[2][0].isdigit()):

        inf = int(data[0][1:-1])
        ram = float("{:.3f}".format(float(data[1][1:-1])))
        rom = float("{:.3f}".format(float(data[2][1:-1])))
    else:
        inf = 0
        ram = 0
        rom = 0
    input.close()
    return inf,ram,rom;

def find_best_fire_density(file_, max_window, skip1, skip2):

    thresh = 0.6 #starting from a threshold of 0.1
    max_range = -999
    min_range = math.floor(max_window/5)
    min_max = 100

    print('\nEvaluating best fire_density threshold:')

    while thresh < 1:
        inferences = load_input(file_, thresh)
        min, max, minw,maxw= fire_density(inferences, max_window, skip1, skip2)
        inf_range = min[0]-max[0]
        score_range = min[2]-max[2]
        if inf_range >= min_range and max[0] < min_max:
            max_range = inf_range
            min_max = max[0]
            best_range = inf_range
            best_thresh = thresh
            best_score_range = score_range
            min_d = min[0]
            max_d = max[0]
            min_s = min[2]
            max_s = max[2]
        thresh+=0.01

    print("\nBest threshold found " + str(float("{:.3f}".format(best_thresh))) + " - Margin: " + str(best_range) + " - Score Margin: " + str(float("{:.3f}".format(best_score_range))))
    print('Min fire density while playing fire ' + str(min_d) + '/' + str(max_window) + ' with an avg window fire score of ' + str(min_s))
    print('Max fire density while playing noise ' + str(max_d) + '/' + str(max_window) + ' with an avg window fire score of ' + str(max_s)+ "\n")

def find_best_consec_fire(file_, max_window, skip1, skip2):

    thresh = 0.6 #starting from a threshold of 0.1

    min_cons_fire_while_fire = 0
    max_cons_fire_while_noise = 0

    cons_fire_while_fire = 0
    cons_fire_while_noise = 0

    when_fire = 0
    when_noise = 0
    max_range = 2
    best_thresh = 0
    min_low = 100

    best_minw = []
    best_maxw = []

    avg_noise_score = 0
    avg_fire_score = 0

    best_thresh = 0
    best_minw = 0
    best_maxw = 0
    best_min_cons_fire_while_fire = 0
    best_max_cons_fire_while_noise = 0

    max_avg_diff = -1

    print('Evaluating best cons_fire threshold:')

    while thresh < 1:

        inferences = load_input(file_, thresh)
        min, max, minw, maxw = fire_density(inferences, max_window, skip1, skip2)

        for noise in maxw:

            if noise.type != "N":
                cons_fire_while_noise +=1

            if noise.type == "N":
                cons_fire_while_noise = 0

            if cons_fire_while_noise > max_cons_fire_while_noise:
                max_cons_fire_while_noise = cons_fire_while_noise
                when_noise = noise.end

        for fire in minw:

            if fire.type != "N":
                cons_fire_while_fire +=1

            if fire.type == "N":
                cons_fire_while_fire = 0

            if cons_fire_while_fire > min_cons_fire_while_fire:
                min_cons_fire_while_fire = cons_fire_while_fire
                when_fire = fire.end
        #print(min_cons_fire_while_fire-max_cons_fire_while_noise)

        if min_cons_fire_while_fire-max_cons_fire_while_noise >= max_range and max_cons_fire_while_noise <= min_low:
            min_low = max_cons_fire_while_noise
            best_thresh = thresh
            best_minw = minw
            best_maxw = maxw
            best_min_cons_fire_while_fire = min_cons_fire_while_fire
            best_max_cons_fire_while_noise = max_cons_fire_while_noise

        thresh += 0.001
        max_cons_fire_while_noise = 0
        min_cons_fire_while_fire = 0
        consec_fire_while_noise = 0
        consec_fire_while_fire = 0

    print("\nBest threshold found " + str(float("{:.3f}".format(best_thresh))) + " - Margin: " + str(best_min_cons_fire_while_fire - best_max_cons_fire_while_noise ))
    print('Max cons. fire while noise ' + str(best_max_cons_fire_while_noise) + ' at ' + str(when_noise))
    print('Min cons. fire while fire ' + str(best_min_cons_fire_while_fire) + ' at ' + str(when_fire))
    print('\nWorst Fire Window:')
    #for i in best_minw:
    #    print(i.type, end = ' ')
    print('\nWorst Noise Window:')
    #for i in best_maxw:
    #    print(i.type , end = ' ')
    print('')

path = os.path.dirname(os.path.abspath(__file__))
data_folder=path+"/model_inf/"
os.system("chmod +rwx " + data_folder)

file1 = data_folder + "1-MFE-CONV1D-2C.txt"
file2 = data_folder + "2-MFE-CONV2D-2C.txt"
file3 = data_folder + "3-SPECTRO-CONV1D-2C.txt"
file4 = data_folder + "4-MFE-CONV1D-4C.txt"
file5 = data_folder + "5-SPECTRO-CONV2D-4CV1.txt"
file6 = data_folder + "6-SPECTRO-CONV2D-4CV2.txt"

file1_window = 20
file1_skip1 = [-4]
file1_skip2 = [3]

file2_window = 30
file2_skip1 = [-4]
file2_skip2 = [3]

file3_window = 30
file3_skip1 = [2,-4,-5,-9,-14,15]    #threshold non trovato
file3_skip2 = [3,5,-3]

file4_window = 20
file4_skip1 = [-13,-12,-4,-2]
file4_skip2 = [3]

file5_window = 35
file5_skip1 = [8,-7,-4,-2]
file5_skip2 = [-11]

file6_window = 30
file6_skip1 = [-4]
file6_skip2 = [3]

#MFECONV1D2C -4 ; 3 - THRESH = 0.71
#SPECTROCONV2D4CV2 -4 ; 3 THRESH = 0.28
'''
inferences = load_input(file5, 0.6)
min, max, min_window, max_window = fire_density(inferences, file5_window, file5_skip1, file5_skip2)

print('\n---------------- '+ file5 + " Window size of " + str(file5_window) + "-------------------------------------")

print('\nMin fire density while playing fire ' + str(min[0]) + '/' + str(file5_window) +  " at " +str(min[1]) + ' with an avg window fire score of ' + str(min[2]) + "\n")

for i in range(0 ,len(min_window),1):
    print(min_window[i].type, end = ' ')
print('\n')

print('Max fire density while playing noise ' + str(max[0]) + '/' + str(file5_window) +  " at " +str(max[1]) + ' with an avg window fire score of ' + str(max[2]) + "\n")

for i in range(0 ,len(max_window),1):
    print(max_window[i].type, end=' ')
print('\n')

'''
print('\n-------------------------------------- ' + file1 + '-----------------------------')
#find_best_consec_fire(file1, file1_window, file1_skip1, file1_skip2)
#find_best_fire_density(file1, file1_window, file1_skip1, file1_skip2)

print('\n-------------------------------------- ' + file2 + '-----------------------------')
find_best_consec_fire(file2, file2_window, file2_skip1, file2_skip2)
find_best_fire_density(file2, file2_window, file2_skip1, file2_skip2)

print('\n-------------------------------------- ' + file3 + '-----------------------------')
find_best_consec_fire(file3, file3_window, file3_skip1, file3_skip2)# non funziona
find_best_fire_density(file3, file3_window, file3_skip1, file3_skip2)

print('\n-------------------------------------- ' + file4 + '-----------------------------')
find_best_consec_fire(file4, file4_window, file4_skip1, file4_skip2)
find_best_fire_density(file4, file4_window, file4_skip1, file4_skip2)

print('\n-------------------------------------- ' + file5 + '-----------------------------')
find_best_consec_fire(file5, file5_window, file5_skip1, file5_skip2)
find_best_fire_density(file5, file5_window, file5_skip1, file5_skip2)

print('\n-------------------------------------- ' + file6 + '-----------------------------')
find_best_consec_fire(file6, file6_window, file6_skip1, file6_skip2)
find_best_fire_density(file6, file6_window, file6_skip1, file6_skip2)
