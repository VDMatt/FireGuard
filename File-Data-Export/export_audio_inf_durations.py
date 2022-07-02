
import sys
import os
import datetime
import csv

class Inference:
    #hold start and end timestamp for each inference
    def __init__(self, startm, starts):

        self.start   = datetime.time(0,startm,starts)

def load_input(file, threshold_):

    frame_index=0

    input = open(file,"r")
    data = input.readlines()

    inferences = []

    for line in data:

        if line[0].isdigit():

            startmin = int(line[0:2])
            startsec = int(line[3:5])

            inf     = Inference(startmin, startsec)
            # getting in which inference the frame belongs
            inferences.append(inf)

        else:
            continue

    input.close()
    return inferences

inference = load_input('1-MFE-CONV1D-2C.txt', 0.808)



with open( 'audio_inf_durations.csv', 'w+', encoding='UTF8') as f:
    writer = csv.writer(f)
    for count in range(1,len(inference),1):

        A = datetime.datetime.combine(datetime.date.today(), inference[count].start)
        B = datetime.datetime.combine(datetime.date.today(), inference[count-1].start)

        seconds = A-B
        seconds = seconds.total_seconds()
        line = [seconds]
        writer.writerow(line)
