# FireGuard
This prototype recognizes and signals the presence of fires in forest environments using two machine learning algorithms, one for the analysis of audio signals, the other for image processing. Both are run on an Arduino Portenta H7 equipped with a Portenta Vision Shield. </br>This microcontroller has two cores: one is used for running the audio network, the other is used for running the video network and managing other peripherals.</br></br>
![Immagine](https://user-images.githubusercontent.com/56454542/176997688-0222fede-92d0-47c0-acdc-cff05f71f105.png)
</br></br>
The device takes audio data as input and runs a convolutional neural network to classify the sample, two classes were defined: "Fire" and "Not-Fire". If the audio sample is classified as fire, a picture is taken and the image is fed into another CNN (MobileNet by Google) that classifies the sample between the same two classes. If the image is classified as "Fire", an alarm is sent using LoRaWAN technology.


## Dataset creation

With the aim of recognizing forest fires, two datasets were created: one containing audio files lasting 5 seconds each, the other containing images.

### Audio dataset

The audio dataset contains 2800 samples, divided equally between the two classes "Fire" and "Not-Fire".</br>
"Not-Fire" class includes the typical sounds of the destination environment: noises of birds, noises of insects, noises of leaves shaken by the wind, sound of rain, etc.</br>
"Fire" class samples were made by digitally overlapping the "Non-Fire" class sounds with samples in which only the sound of fire was reproduced at different intensities. In addition, some samples were recorded during the burning of plant residues, holding the microphone at varying distances.

### Video dataset

The video dataset contains 5000 images, divided equally between the two classes "Fire" and "Not-Fire".</br>
"Not-Fire" class includes images of forest environments in various weather and light conditions.</br>
"Fire" class samples contains images of forest fires of varying intensity, both during the day and during the night.

## Neural Networks

The steps of designing the neural network, training of the network and generating the necessary code to make the algorithms run on the microcontroller were made on the [EdgeImpulse](https://www.edgeimpulse.com/) platform. </br>
The classification of the audio samples is carried out by a convolutional neural network that uses the MEL coefficients to extract features from audio data. </br>
A CNN architecture developed by google (MobileNet) was used for the image classification.


| Category | Precision (test set) |
| ---      | ---       |
| Audio | 90.7% |
| Video (RGB input) | 95.1%  |
| Video (Grayscale input) | 82.6% |

The camera supplied with the Portenta H7 captures grayscale images, which is why a model that takes grayscale images as input has been used. 

## On-Device Test

A test has been designed to verify the correct functioning of the device: an hour-long audio file has been created in which sections of "Fire" and "Non-Fire" alternate at intervals of 2-4 minutes. </br>
A slide show was created on the audio file in which images of forest fires alternate with images of forest environments in normal conditions. The images have the same context of the reproduced sounds so that the fire is shown while playing a section of class "Fire" and vice versa. </br>
"Fire" sections were further divided according to the intensity of the fire:</br>
- Low Noise Test (LNT): the sound of fire is higher than that of background noises and the fire is the main element of the shot. </br>
![lnt](https://user-images.githubusercontent.com/56454542/177165157-22451199-f143-4aff-9e76-b7eb5e9fb7fb.png)

- Mild Noise Test (LNT): the sound of fire is equivalent to the background noises' one and there is a fire modest in size but clearly visible. </br>
![mnt](https://user-images.githubusercontent.com/56454542/177165644-528d6161-cb9b-4d70-8f3a-1c6841ca1ba3.png)

- Extreme Noise Test (LNT): the sound of fire is lower than that of the background noises and there is a small fire in the picture. </br>
![ent](https://user-images.githubusercontent.com/56454542/177165961-7a205fb2-febc-43ed-b8dd-d3ba5c1bebfb.png)
</br>
During the test, the device continuously made inferences (data acquisition, neural network execution, saving of results). The test sounds were reproduced using a 40W passive speaker, placing the Arduino at a distance of 1m from it. The slideshow was played on a monitor with minimum brightness and maximum saturation settings, the Arduino was positioned a few centimeters from the monitor so that the camera's field of view included exactly the image shown.</br>

Test files are available [here](https://drive.google.com/drive/u/1/folders/1mRyWbie1wNAD0EH5crP4WQwU5xWOfcy1).


### Alarm Conditions

On the basis of the test results, in particular on the basis of the "Fire" class probability associated with each inference, alarm conditions were defined. These are intended to limit the reporting of false positives while keeping that of true positives as high as possible, alarms conditions also need to be calibrated to detect a forest fire as quickly ass possible. Based on some test, these alarm conditions were defined:

- Audio CNN: two consecutive inferences with p(fire)>= 0.808
- Video CNN: four consecutive inferences with p(fire)>= 0.823


### Test Results

The test results are shown in a graph that plots the probability of "Fire" class over time with a blue line. The time axis is divided into the various test sections: Noise (or "Not-Fire) with a green background, LNT with a yellow background, MNT with a magenta background, ENT with a gray background. </br>
The red lines are drawn in the instants in which the alarm conditions are satisfied.
</br>
#### Audio CNN test results
![AudioNN](https://user-images.githubusercontent.com/56454542/177169338-190c8522-1759-4e1f-a9dc-91345296430b.png)

</br>

#### Video CNN test results

![VideoNN](https://user-images.githubusercontent.com/56454542/177171105-efa7a9ef-b540-49b0-b4a6-8fd7755f9ff7.png)

</br>
</br>


The last test was done using the models jointly, like this: if the alarm conditions for the audio network were met, the video network was activated which recorded the final alarm if the alarm conditions for the video network were also satisfied.</br>

Based on these results, the definitive evaluation metrics for every use-case (audio network only, video network only, both networks together) were defined:

- True positives: number of alarms triggered during the "Fire" class sections;
- False positives: number of alarms triggered during the "Not-Fire" class sections;
- True negatives: number of sections of "Not-Fire" in which the alarm didn't trigger;
- False negatives: number of sections of "Fire" in which the alarm didn't trigger;
- Alarm delay: based on the timestamp in which a test section was changing, alarm latencies were calculated.

</br>

![modelliconfronto](https://user-images.githubusercontent.com/56454542/177191937-233d0ae0-12bf-4b85-b9db-ba0acd21c31c.png)

![AAlarmCDF](https://user-images.githubusercontent.com/56454542/177192731-b267645a-9607-498e-b4ec-d759bef154e7.png)
![VAlarmCDF](https://user-images.githubusercontent.com/56454542/177192729-0eeb180f-e6ef-4b13-b384-c3fcde75b1eb.png)
![AVAlarmCDF](https://user-images.githubusercontent.com/56454542/177192727-8adc2ef2-a29e-4f5c-b1f6-cede61455a05.png)

#### Test conclusions
The audio network is particularly efficient at recognizing true negatives, and has an average alarm latency of around 25 seconds.</br>
The video network is the fastest with an alarm latency of around 20 seconds and it is particularly efficient in detecting false positives, but it can handle a considerable number of false negatives.</br>
Using the networks jointly involves an expansion of the alarm latency which is fully compensated by the overall increase in precision of the system.</br>

## Additional features

- Saving images: all the images taken by the device are saved on an SD card in a text file as pixel matrices, these can be compressed in standard formats using a computer and they can be used to expand the dataset.
- Alarm signaling: the alarm signaling is done through the LoRaWAN protocol. It is a low cost and low power consumption protocol.
- The signaling packet includes the mean and standard deviation of the p(fire) associated with the inferences that triggered the alarms (both for the audio network and for the video network). These values give an indication of how likely a forest fire is: a high standard deviation is can indicate uncertain measurements, conversely a low standard deviation could indicate that the alarm is not a false positive.
