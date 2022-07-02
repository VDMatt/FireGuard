# FireGuard
This prototype recognizes and signals the presence of fires in forest environments using two machine learning algorithms, one for the analysis of audio signals, the other for image processing. Both are run on an Arduino Portenta H7 equipped with a Portenta Vision Shield.</br></br>
![Immagine](https://user-images.githubusercontent.com/56454542/176997688-0222fede-92d0-47c0-acdc-cff05f71f105.png)
</br></br>
The device takes audio data as input and runs a convolutional neural network to classify the sample, two classes were defined: "Fire" and "Not-Fire". If the audio sample is classified as fire, a picture is taken and the image is fed into another CNN (MobileNet by Google) that classifies the sample between the same two classes. If also the image is classified as "Fire", an alarm is sent using LoRaWAN.


## Dataset creation

With the aim of recognizing forest fires, two datasets were created: one containing audio files lasting 5 seconds each, the other containing images.

### Audio dataset

The Audio dataset contains 2800 samples, divided
