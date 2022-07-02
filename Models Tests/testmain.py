
import sys
import os
import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import roc_curve
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

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
        self.type   = type

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
def load_input(file, treshold):

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

            if fscore > treshold:
                pred = "F"
                score = fscore
            if fscore < treshold:
                pred = "N"
                score = nscore
            if fscore == treshold:
                pred = "D"
                score = 0
    
            inf      = Inference(startmin, startsec, endmin, endsec, pred, score)
            inferences.append(inf)

        else:
            continue
    input.close()
    return inferences

def compute_results(data, plotting):

    frame_index=0
    noise_results = []
    fire_results  = []
    invalid = []
    uncertain = []
    max_consecutive_fire_while_fire = 0
    max_consecutive_fire_while_noise = 0
    consecutive_fire_while_fire = []
    consecutive_fire_while_noise = []
    last_consecutive_index = 0
    consec_fire = 0


    for count, inf in enumerate(inferences):

        if inf.start>=rexpected[frame_index].end:
            while inf.start>=rexpected[frame_index].start:
                if inf.start<rexpected[frame_index].end or (inf.end<=rexpected[frame_index].end and inf.start>=rexpected[frame_index].start):
                    break
                frame_index+=1
            consec_fire=1
            last_consecutive_index = count

        if (inf.start<rexpected[frame_index].end and inf.end>rexpected[frame_index].end) or rexpected[frame_index].type=="Invalid":
            tuple = ("Invalid", str(inf.start), str(inf.end))
            invalid.append(tuple)
        else:
            tuple = (rexpected[frame_index].type, inf.Fconf, inf.Nconf,str(inf.start),str(inf.end))
            #consectutive fire results algorithm
            if inf.type=="F":

                consec_fire = 1
                fire_results.append(tuple)

                if count>=last_consecutive_index:

                    for i in range(0, len(inferences)-count-1,1):

                        last_consecutive_index += 1

                        if inferences[count+i+1].type != "N" and inferences[count+i+1].start<rexpected[frame_index].end:
                            consec_fire += 1

                        if  inferences[count+i+1].type == "N" or inferences[count+i+1].start>rexpected[frame_index].end or last_consecutive_index >= len(inferences)-1:
                            if rexpected[frame_index].type == "ENT" or rexpected[frame_index].type == "MNT" or rexpected[frame_index].type == "LNT":
                                if consec_fire > max_consecutive_fire_while_fire:
                                    max_consecutive_fire_while_fire=consec_fire
                                consecutive_fire_while_fire.append(consec_fire)
                            elif rexpected[frame_index].type == "Noise":
                                if consec_fire > max_consecutive_fire_while_noise:
                                    max_consecutive_fire_while_noise=consec_fire
                                consecutive_fire_while_noise.append(consec_fire)
                            break



            elif inf.type=="N":
                noise_results.append(tuple)
                last_consecutive_index += 1
            elif inf.type=="D":
                uncertain.append(tuple)
                last_consecutive_index += 1
            if count == len(inferences)-1 and inferences[-1].type == "F" and inferences[-2].type != "F" and rexpected[frame_index].type != "Noise":
                consecutive_fire_while_fire.append(1)
            elif count == len(inferences)-1 and inferences[-1].type == "F" and inferences[-2].type != "F" and rexpected[frame_index].type == "Noise":
                consecutive_fire_while_noise.append(1)

    #calculate test statistics

    inf_while_fire  = 0
    inf_while_noise = 0
    inf_while_ENT  = 0
    inf_while_MNT  = 0
    inf_while_LNT  = 0

    noise_while_ENT = 0

    uncertain_while_fire  = 0
    uncertain_while_noise = 0

    avg_fire_while_fire    = []
    avg_noise_while_noise  = []

    avg_fire_while_LNT   = []
    avg_fire_while_MNT   = []
    avg_fire_while_ENT   = []

    avg_noise_while_fire   = []
    avg_fire_while_noise   = []


    for i in range(0,len(fire_results),1):

        if fire_results[i][0] == "ENT" or fire_results[i][0] == "MNT" or fire_results[i][0] == "LNT":

            inf_while_fire  += 1
            avg_fire_while_fire.append(fire_results[i][1])

            if fire_results[i][0] == "ENT":
                inf_while_ENT  += 1
                avg_fire_while_ENT.append(fire_results[i][1])
            if fire_results[i][0] == "MNT":
                inf_while_MNT+=1
                avg_fire_while_MNT.append(fire_results[i][1])
            if fire_results[i][0] == "LNT":
                inf_while_LNT+=1
                avg_fire_while_LNT.append(fire_results[i][1])

        elif fire_results[i][0] == "Noise":

            inf_while_noise  += 1
            avg_fire_while_noise.append(fire_results[i][1])

    for i in range(0,len(noise_results),1):

        if   noise_results[i][0] == "ENT" or noise_results[i][0] == "MNT" or noise_results[i][0] == "LNT":

            inf_while_fire   += 1
            avg_noise_while_fire.append(noise_results[i][2])

            if noise_results[i][0] == "ENT":
                inf_while_ENT+=1
                noise_while_ENT+=1
            if noise_results[i][0] == "MNT":
                inf_while_MNT+=1
            if noise_results[i][0] == "LNT":
                inf_while_LNT+=1

        elif noise_results[i][0] == "Noise":

            inf_while_noise += 1
            avg_noise_while_noise.append(noise_results[i][2])


    for i in range(0,len(uncertain),1):

        if  uncertain[i][0] == "ENT" or uncertain[i][0] == "MNT" or uncertain[i][0] == "LNT":
            inf_while_fire +=  1
            uncertain_while_fire += 1

        elif uncertain[i][0] == "Noise":
            inf_while_noise += 1
            uncertain_while_noise += 1

    mean_fire_while_fire   = avg(avg_fire_while_fire)
    mean_noise_while_noise = avg(avg_noise_while_noise)
    mean_fire_while_ENT  = avg(avg_fire_while_ENT)
    mean_fire_while_MNT  = avg(avg_fire_while_MNT)
    mean_fire_while_LNT  = avg(avg_fire_while_LNT)
    mean_noise_while_fire  = avg(avg_noise_while_fire)
    mean_fire_while_noise  = avg(avg_fire_while_noise)

    LNT_perc = 0
    MNT_perc = 0
    ENT_perc = 0
    valid_perc = 0
    good_fire_percentage = 0
    bad_fire_percentage  = 0
    good_noise_percentage = 0
    bad_noise_percentage = 0
    uncertain_percentage = 0
    uncertain_fire_percentage = 0
    uncertain_noise_percentage = 0

    true_positives = len(avg_fire_while_fire)
    true_positives_nof1 = len(avg_fire_while_fire) - len(avg_fire_while_ENT)
    true_negatives = len(avg_noise_while_noise)
    false_positives = len(avg_fire_while_noise)
    false_negatives = len(avg_noise_while_fire)
    false_negatives_nof1 = len(avg_noise_while_fire) - noise_while_ENT
    tot_inferences     = len(inferences) #numero totale di inferenze (valide e non)
    valid_inferences   = len(inferences)-len(invalid)

    if tot_inferences != 0:
        valid_perc         = float("{:.1f}".format((valid_inferences/tot_inferences)*100))
    if inf_while_fire != 0:
        fire_accuracy  = float("{:.1f}".format((true_positives/inf_while_fire)*100))
        fire_accuracy_nof1  = float("{:.1f}".format((true_positives_nof1/(inf_while_fire-inf_while_ENT))*100))
        false_negatives_percentage   = float("{:.1f}".format((false_negatives/inf_while_fire)*100))
        uncertain_fire_percentage  = float("{:.1f}".format((uncertain_while_fire/inf_while_fire)*100))
    if inf_while_noise != 0:
        noise_accuracy = float("{:.1f}".format((true_negatives/inf_while_noise)*100))
        false_positives_percentage  = float("{:.1f}".format((false_positives/inf_while_noise)*100))
        uncertain_noise_percentage  = float("{:.1f}".format((float(uncertain_while_noise)/float(inf_while_noise))*100))
    if valid_inferences != 0:
        uncertain_percentage  = float("{:.1f}".format((float(uncertain_while_fire + uncertain_while_noise)/float(valid_inferences))*100))
    if (inf_while_fire + inf_while_noise) != 0:
        accuracy = float("{:.1f}".format(((true_positives + true_negatives)/(inf_while_fire + inf_while_noise))*100))
        accuracy_nof1 = float("{:.1f}".format((fire_accuracy_nof1+noise_accuracy)/2))
    if (false_positives + false_negatives) !=0:
        recall = float("{:.1f}".format((true_positives/(true_positives+false_negatives))*100))
        recall_nof1 = float("{:.1f}".format((true_positives_nof1/(true_positives_nof1 + false_negatives_nof1))*100))
    if (true_positives + false_positives) != 0:
        precision = float("{:.1f}".format((true_positives/(true_positives+false_positives))*100))
        precision_nof1 = float("{:.1f}".format((true_positives_nof1/(true_positives_nof1+false_positives))*100))
    if recall != 0 and precision != 0:
        F1 = float("{:.1f}".format((2/((1/recall)+(1/precision)))))
        F1_nof1 = float("{:.1f}".format((2/((1/recall_nof1)+(1/precision_nof1)))))

    if inf_while_LNT != 0:
        LNT_perc         = float("{:.1f}".format((len(avg_fire_while_LNT)/inf_while_LNT)*100))
    if inf_while_MNT != 0:
        MNT_perc         = float("{:.1f}".format((len(avg_fire_while_MNT)/inf_while_MNT)*100))
    if inf_while_ENT != 0:
        ENT_perc         = float("{:.1f}".format((len(avg_fire_while_ENT)/inf_while_ENT)*100))
    if (inf_while_fire-inf_while_ENT)!= 0:
        false_neg_perc = float("{:.1f}".format(((false_negatives-noise_while_ENT)/(inf_while_fire-inf_while_ENT))*100))

    #treshold optimization

    y_test = []
    y_pred_proba = []

    for i in range(0,len(inferences),1):
        if i <= len(fire_results)-1:
            if fire_results[i][0] == "ENT" or fire_results[i][0] == "MNT" or fire_results[i][0] == "LNT":
                y_test.append(1)
                y_pred_proba.append(fire_results[i][1])
            elif fire_results[i][0] =="Noise":
                y_test.append(0)
                y_pred_proba.append(fire_results[i][1])
        if i<= len(noise_results)-1:
            if noise_results[i][0] == "ENT" or noise_results[i][0] == "MNT" or noise_results[i][0] == "LNT":
                y_test.append(1)
                y_pred_proba.append(noise_results[i][1])
            elif noise_results[i][0] =="Noise":
                y_test.append(0)
                y_pred_proba.append(noise_results[i][1])
        if i> len(fire_results) and i>len(noise_results):
            break


    #treshold optimization
    #ROC curve
    fpr, tpr, thresholds = metrics.roc_curve(y_test,  y_pred_proba)
    #precision/recall
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)

    if plotting:
        #create ROC curve
        plt.plot(fpr,tpr)
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.show()
        # plot the roc curve for the model
        plt.plot(recalls, precisions, marker='.', label='Logistic')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.legend()
        plt.show()

    # get the best threshold for ROC
    J = tpr - fpr
    ix = np.argmax(J)
    best_thresh = thresholds[ix]
    auc = metrics.roc_auc_score(y_test, y_pred_proba)

    # get the best threshold for PR
    fscore = (2 * precisions * recalls) / (precisions + recalls)
    # locate the index of the largest f score
    pr = np.argmax(fscore)
    best_pr = thresholds[pr]

    results = []
    results.append(accuracy_nof1) #0
    results.append(accuracy)
    results.append(recall_nof1)
    results.append(recall)
    results.append(precision_nof1)
    results.append(precision) #5
    results.append(F1_nof1)
    results.append(F1)
    results.append(fire_accuracy_nof1)
    results.append(fire_accuracy)
    results.append(mean_fire_while_fire) #10
    results.append(false_neg_perc)
    results.append(false_negatives_percentage)
    results.append(mean_noise_while_fire)
    results.append(noise_accuracy)
    results.append(mean_noise_while_noise) #15
    results.append(false_positives_percentage)
    results.append(mean_fire_while_noise)
    results.append(LNT_perc)
    results.append(MNT_perc)
    results.append(ENT_perc) #20
    results.append(max_consecutive_fire_while_fire)
    results.append(avg(consecutive_fire_while_fire))
    results.append(max_consecutive_fire_while_noise)
    results.append(avg(consecutive_fire_while_noise))
    results.append(tot_inferences) #25
    results.append(valid_inferences)
    results.append(uncertain_while_fire)
    results.append(uncertain_fire_percentage)
    results.append(uncertain_while_noise)
    results.append(uncertain_noise_percentage) #30
    results.append(mean_fire_while_LNT)
    results.append(mean_fire_while_MNT)
    results.append(mean_fire_while_ENT) #33
    results.append(auc)
    results.append(best_pr) #35

    return results

def color(value):

    if value >0:
        value = "(\033[92m\033[1m+"+str(value)+"\033[0m)"
    elif value <0:
        value = "(\033[91m\033[1m"+str(value)+"\033[0m)"
    else:
        value = "(\033[1m"+str(value)+"\033[0m)"
    return value

def compute_delta(from_, to):
    delta = []
    for i in range (0, len(from_)-2,1):
        #print( str(to[i])+ "-" + str(from_[i]))
        value = float("{:.3f}".format(to[i] - from_[i]))
        value = color(value)
        delta.append(value)
    return delta

def print_results(name, inf, RAM, ROM, from_, to, deltas):

    print("\n\n----------------------------------"+ name +"-----------------------------------------\n")
    print("Inferencing Time: "+ str(inf) + "ms  RAM Usage: "+ str(RAM) + "Kb  ROM Usage : " + str(ROM) + "Kb\n")
    print("Inferences done: "+ str(from_[25]) + "  Valid inferences:"+ str(float("{:.1f}".format((from_[26]/from_[25])*100)))+"%\n")
    print("Accuracy:  " + str(from_[1]) + deltas[1])
    print("Recall:    " + str(from_[3]) + deltas[3])
    print("Precision: " + str(from_[5]) + deltas[5])
    print("F1:        " + str(from_[7]) + deltas[7])
    print("\nOptimal threshold found: " + str(from_[35]) + "    AUC(ROC): " + str(float("{:.3f}".format(from_[34]))))
    print("\nTrue Positives:  " +str(from_[9]) +  deltas[9] + ", mean score: " + str(from_[10]) + deltas[10])
    print("False negatives: " +str(from_[12]) + deltas[12] + ", mean score:" + str(from_[13])+ deltas[13])
    print("\nTrue Negatives: " + str(from_[14]) + deltas[14] + ", mean score: " + str(from_[15]) + deltas[15])
    print("False positives: " + str(from_[16]) + deltas[16] + ", mean score: " + str(from_[17]) + deltas[17])
    print("\nUncertain while fire: " + str(from_[27]) + deltas[27] + " Uncertain while noise: " + str(from_[29]) + deltas[29])
    print("\nFire volume dominance accuracy: " + str (from_[18]) +  deltas[18])
    print("Fire = Noise volume accuracy:  " + str (from_[19])  +  deltas[19])
    print("ENT accuracy: " + str (from_[20])+ deltas[20])
    print("\nMax cons. fire while fire: " + str(from_[21]) + deltas[21] + " and avg. cons. " + str(from_[22])+ deltas[22])
    print("Max cons. fire while noise: " + str(from_[23]) + deltas[23] + " and avg. cons. " + str(from_[24]) + deltas[24])

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



path = os.path.dirname(os.path.abspath(__file__))
data_folder=path+"/model_inf"
os.system("chmod +rwx " + data_folder)
enc_data_folder = os.fsencode(data_folder)
files = os.listdir(enc_data_folder)
for file in files:
    filename = os.fsdecode(file)
    os.system("chmod +rwx " + data_folder + "/" +filename)
    file = data_folder+"/" + filename
    inf,ram,rom = get_model_info(file)
    inferences = load_input(file, 0.75)
    results = compute_results(inferences, 0)
    opt_tresh = results[35]
    inferences = load_input(file, opt_tresh)
    opt_results = compute_results(inferences, 0)
    variation = compute_delta(results,opt_results)
    name = filename[2:-4]
    print_results(name, inf, ram, rom, results, opt_results, variation)
