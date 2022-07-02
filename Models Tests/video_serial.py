import serial
import datetime
from datetime import timedelta
import sys
import os

start_time = datetime.datetime.now()
ser = serial.Serial("/dev/ttyS6")
ser.flushInput()
path = os.path.dirname(os.path.abspath(__file__))
output = path+"/video_inferences.txt"
print(output)
output = open(output,"w+")
inferences = 0
timestamp = datetime.datetime.now()
#In questo modo salvo in CSV
output.write("Timestamp,F_Score,Photo ID,Expected_outcome"+"\n")
current_frame_index = 0

class Frame:

    #hold start and end timestamp for each frame
    def __init__(self, startm, starts, endm, ends, type):

        self.start   = datetime.time(0,startm,starts)
        self.end     = datetime.time(0,endm,ends)
        self.type    = type

    def print(self):
        print("Sample type: " + self.type +" "+ str(self.start)+"-"+str(self.end))

test_frames = []

# test frames definition
frame = Frame(0,0,0,15,"Invalid")
test_frames.append(frame)
frame = Frame(0,16,2,15,"Noise") #birds
test_frames.append(frame)
frame = Frame(2,16,4,15,"LNT") #birds + LNT
test_frames.append(frame)
frame = Frame(4,16,6,15,"Noise") #crickets
test_frames.append(frame)
frame = Frame(6,16,8,15,"LNT") #crickets + LNT
test_frames.append(frame)
frame = Frame(8,16,10,15,"Noise") #rain
test_frames.append(frame)
frame = Frame(10,16,12,15,"Noise") #wind
test_frames.append(frame)
frame = Frame(12,16,14,15,"Noise") #birds
test_frames.append(frame)
frame = Frame(14,16,16,15,"LNT") #birds + LNT
test_frames.append(frame)
frame = Frame(16,16,18,15,"Noise") #insects
test_frames.append(frame)
frame = Frame(18,16,20,15,"LNT") #insects + LNT
test_frames.append(frame)
frame = Frame(20,16,22,15,"Noise") #rain
test_frames.append(frame)
frame = Frame(22,16,24,15,"Noise") #wind
test_frames.append(frame)
frame = Frame(24,16,26,15,"LNT") #Campfire
test_frames.append(frame)
frame = Frame(26,16,28,15,"MNT") #birds + MNT
test_frames.append(frame)
frame = Frame(28,16,30,15,"MNT") #birds + MNT
test_frames.append(frame)
frame = Frame(30,16,32,15,"Noise") #birds
test_frames.append(frame)
frame = Frame(32,16,34,15,"Noise") #insects
test_frames.append(frame)
frame = Frame(34,16,36,15,"LNT") #campfire
test_frames.append(frame)
frame = Frame(36,16,40,15,"Noise") #rain
test_frames.append(frame)
frame = Frame(40,16,44,15,"MNT") #insects + MNT
test_frames.append(frame)
frame = Frame(44,16,46,15,"Noise") #wind
test_frames.append(frame)
frame = Frame(46,16,48,15,"ENT") #birds + ENT
test_frames.append(frame)
frame = Frame(48,16,50,15,"ENT") #birds + ENT
test_frames.append(frame)
frame = Frame(50,16,54,15,"Noise") #rain
test_frames.append(frame)
frame = Frame(54,16,58,15,"ENT") #insects + ENT
test_frames.append(frame)
frame = Frame(58,16,59,59,"LNT") #Campfire
test_frames.append(frame)


try:

    while True:

        ser_bytes = ser.readline()
        #output dell'arduino, che stampa in seriale F_score e photo_ID separati da una virgola
        arduino_output = ser_bytes.decode("utf-8")

        #Arduino stampa "Taking photo" prima di scattare la foto
        if arduino_output.startswith("Taking"):
            timestamp = datetime.datetime.now() - timedelta(hours = start_time.hour,minutes = start_time.minute,seconds=start_time.second)

            #Controlla che non si siano superati i limiti orari del test
            if rec_end.hour == 1 and rec_end.second >= 0:

                print("Test terminated.")
                output.close()
                sys.exit()

        elif arduino_output.startswith("*"):

            if timestamp.second<10:
                start_s="0"+str(timestamp.second)
            else:
                start_s = str(timestamp.second)
            if timestamp.minute<10:
                start_m="0"+str(timestamp.minute)
            else:
                start_m = str(timestamp.minute)

            timestamp = datetime.time(0,start_m,start_s)

            #Se la foto è stata scattata dopo il frame corrente, aumento frame index per aggiornare Expected_outcome (test_frames[current_frame_index].type)
            if timestamp > test_frames[current_frame_index]:
                current_frame_index+=1

            out=start_m+":"+start_s+","+arduino_output[:-1]+","+test_frames[current_frame_index].type 
            print(out)
            output.write(out+"\n")


except KeyboardInterrupt:

    output.close()

    pass
