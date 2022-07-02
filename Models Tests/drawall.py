from PIL import Image
import numpy as np
import os
foldername = 'video_test_images'
path = os.path.dirname(os.path.abspath(__file__))
data_folder=path+"/video_test_txts"
os.system("chmod +rwx  " + data_folder)
if not os.path.exists(path+'/' + foldername):
    os.makedirs(path+'/' + foldername)
os.system("chmod +rwx  " + path+'/' + foldername)
enc_data_folder = os.fsencode(data_folder)
files = os.listdir(enc_data_folder)
for file in files:

    #Load Pixels from txt file
    filename = os.fsdecode(file)
    os.system("chmod +rwx " + data_folder + "/" +filename)
    file = data_folder + "/" + filename
    array = np.loadtxt(file, dtype=np.uint8, delimiter = ',')
    print(array)
    # Use PIL to create an image from the new array of pixels
    new_image = Image.fromarray(array)
    new_image.save(path + '/'+ foldername +'/'+ filename[:-4] + '.png')
