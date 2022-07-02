import serial
import datetime
from datetime import timedelta
import sys
import os

start_time = datetime.datetime.now()
ser = serial.Serial("/dev/ttyS9")
ser.flushInput()
path = os.path.dirname(os.path.abspath(__file__))
output = path+"/model.txt"
print(output)
output = open(output,"w+")
inferences = 0
rec_start = datetime.datetime.now()
rec_end   = datetime.datetime.now()

try:

    while True:

        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes.decode("utf-8")

        if decoded_bytes.startswith("Inf"):
            rec_start = datetime.datetime.now() - timedelta(hours = start_time.hour,minutes = start_time.minute,seconds=start_time.second)

        elif decoded_bytes.startswith("Do"):
            rec_end   = datetime.datetime.now() - timedelta(hours = start_time.hour,minutes = start_time.minute,seconds=start_time.second)

            #controlla che non si siano superati i limiti orari del test
            if rec_end.hour == 1 and rec_end.second >= 0:

                print("Test terminated.")
                output.close()
                sys.exit()

        elif decoded_bytes.startswith("*"):

            if rec_start.second<10:
                start_s="0"+str(rec_start.second)
            else:
                start_s = str(rec_start.second)
            if rec_start.minute<10:
                start_m="0"+str(rec_start.minute)
            else:
                start_m = str(rec_start.minute)

            if rec_end.second<10:
                end_s="0"+str(rec_end.second)
            else:
                end_s = str(rec_end.second)
            if rec_end.minute<10:
                end_m="0"+str(rec_end.minute)
            else:
                end_m = str(rec_end.minute)

            out=start_m+":"+start_s+"-"+end_m+":"+end_s+decoded_bytes[1:-1] #genera errore ogni tanto
            print(out)
            output.write(out+"\n")


except KeyboardInterrupt:

    output.close()
    pass
