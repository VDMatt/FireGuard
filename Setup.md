# Device Setup

### Hardware/Software Requirements

- [Arduino Portenta H7](https://www.arduino.cc/pro/hardware/product/portenta-h7)
- [Portenta Vision Shield (LoRaWAN](https://store.arduino.cc/products/arduino-portenta-vision-shield-lora%C2%AE)
- [LoRaWAN antenna](https://it.rs-online.com/web/p/arduino-shield/1697591?cm_mmc=IT-PLA-DS3A-_-google-_-CSS_IT_IT_Raspberry_Pi_&_Arduino_e_Strumenti_di_sviluppo_Whoop-_-(IT:Whoop!)+Arduino+-+Shield-_-1697591)
- SD Card
- Arduino IDE

### Running the device

To make the device run, please open [/Arduino Code](https://github.com/VDMatt/FireGuard/tree/main/Arduino%20Code), and add the 3 zipped libraries to your IDE. One is needed to run the audio network, one is needed for the video network, the third
is needed to make the LoRaWAN module work properly using [this fix](https://github.com/arduino-libraries/MKRWAN/pull/93).

- Split the flash memory as 1MB for M7 Core, 1MB for the M4 Core.
- Upload [M4.ino](https://github.com/VDMatt/FireGuard/blob/main/Arduino%20Code/M4_AUDIO/M4_AUDIO.ino) on the M4 Core and [M7.ino](https://github.com/VDMatt/FireGuard/blob/main/Arduino%20Code/M7_VIDEO/M7_VIDEO.ino) on the M7 Core.

