# FireGuard
This prototype recognizes and signals the presence of fires in forest environments using two machine learning algorithms, one for the analysis of audio signals, the other for image processing. Both are run on an Arduino Portenta H7 equipped with a Portenta Vision Shield.</br></br>
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

The camera supplied with the Portenta H7 captures grayscale images, which is why a model that takes grayscale images as input has been designed. 
