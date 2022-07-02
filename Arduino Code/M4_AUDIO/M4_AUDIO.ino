/* Edge Impulse Arduino examples
 * Copyright (c) 2021 EdgeImpulse Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

// If your target is limited in memory remove this macro to save 10K RAM
//#define EIDSP_QUANTIZE_FILTERBANK   0

/* Includes ---------------------------------------------------------------- */
#include <PDM.h>
#include <MFE-CONV1D-2CLASSES_inferencing.h>
#include "SDMMCBlockDevice.h"
#include "FATFileSystem.h"
#include "mbed.h"
#define alarmfile "/fs2/last_alarm.txt"
#define consec_fire_alarm 2

/** Audio buffers, pointers and selectors */
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

uint8_t cons_fire = 0;
static inference_t inference;
static signed short sampleBuffer[2048];
static bool debug_nn = false; // Set this to true to see e.g. features generated from the raw signal
static volatile bool record_ready = false;
bool sd = 0;
float hold1 = 0; //hold p(f) of the last inferences made
float hold2 = 0;
bool warning_mode = 0; //if i hear one fire, enter warning mode: in warning mode 10 consecutive recordings are made without delay to make sure fire is recognized faster
bool warning_count = 0;
SDMMCBlockDevice block_device;
mbed::FATFileSystem fs2("fs2");

void setup()
{   
    pinMode(D4,OUTPUT);//Failed to run classifier debug flag
    pinMode(D9,OUTPUT);//One fire recognized debug flag
    pinMode(D10,OUTPUT);//Alarm flag
    pinMode(D11,INPUT);//Took the picture after alarm, you can go back to listening flag
    pinMode(D12,INPUT);
    digitalWrite(D10, LOW);
    digitalWrite(D9, LOW);
    digitalWrite(D4, LOW);

    delay(3000);
    
    //SD CARD SETUP
    sd =  fs2.mount(&block_device);
    if (sd) {
      sd = fs2.reformat(&block_device);
    }
    if (sd!=0) {
       Serial.println("Error formatting SDCARD ");
    }
    
    if (microphone_inference_start(EI_CLASSIFIER_RAW_SAMPLE_COUNT) == false) {
        ei_printf("ERR: Failed to setup audio sampling\r\n");
        return;
    }
}

/**
 * @brief      Arduino main function. Runs the inferencing loop.
 */
void loop()
{
  
    if(!warning_mode){
      thread_sleep_for(10000);
    }
    
    if(warning_mode){
      delay(100);
      warning_count+=1;    
    } 
    
    //if i hear a fire, and warning mode is not been activated
    if(cons_fire == 1){
      digitalWrite(D9,HIGH);
      if(warning_count == 0){
        warning_mode = 1;
      }       
    }
    //if i hear enough consecutive fires, trigger the alarm 
    if(cons_fire == consec_fire_alarm){
      
        cons_fire = 0;           
        digitalWrite(D10, HIGH);
        //wait for the M7 to read the alarm flag
        while(digitalRead(D11)== LOW){
          delay(1000);
        }
        delay(1000);
         while(digitalRead(D12) == LOW){
          delay(1000);
          }  
            
        //go back to record audio
        
        if(sd==0){ //if sd is correctly initialized
          FILE *fd = fopen(alarmfile, "w+");
          char fscore[15];
          char out[15];
          memset(fscore, 0, sizeof(fscore));
          memset(out, 0, sizeof(out));
          sprintf(fscore, "%.03f-", hold1);
          strcpy(out, fscore);
          sprintf(fscore, "%.03f!", hold2);
          strcat(out, fscore);
          fprintf(fd, out);
          fclose(fd);
        }
        
        digitalWrite(D10, LOW);
        digitalWrite(D9,LOW);
        digitalWrite(D4, LOW);
        warning_mode = 0;
        warning_count = 0;
        
    }

    bool m = microphone_inference_record();
    if (!m) {
        ei_printf("ERR: Failed to record audio...\n");
        return;
    }

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &microphone_audio_signal_get_data;
    ei_impulse_result_t result = { 0 };

    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, debug_nn);
    if (r != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", r);
        digitalWrite(D4,HIGH);
        return;
    }

    if(result.classification[0].value>=0.808){
      cons_fire ++; 
      if(cons_fire == 1){
        hold1 = result.classification[0].value;
        hold2 = 0;
      }
      if(cons_fire == 2){
        hold2 = result.classification[0].value;
      }
    }
    else{
      cons_fire = 0;
      hold1 = 0;
      hold2 = 0;
      digitalWrite(D9, LOW);
      digitalWrite(D4, LOW);    
    }

    if(warning_count == 10){
        warning_mode = 0;
        warning_count = 0;
      }
      
#if EI_CLASSIFIER_HAS_ANOMALY == 1
    ei_printf("    anomaly score: %.3f\n", result.anomaly);
#endif
}

/**
 * @brief      Printf function uses vsnprintf and output using Arduino Serial
 *
 * @param[in]  format     Variable argument list
 */
void ei_printf(const char *format, ...) {
    static char print_buf[1024] = { 0 };

    va_list args;
    va_start(args, format);
    int r = vsnprintf(print_buf, sizeof(print_buf), format, args);
    va_end(args);

    if (r > 0) {
        //Serial.write(print_buf);
    }
}

/**
 * @brief      PDM buffer full callback
 *             Copy audio data to app buffers
 */
static void pdm_data_ready_inference_callback(void)
{
    int bytesAvailable = PDM.available();

    // read into the sample buffer
    int bytesRead = PDM.read((char *)&sampleBuffer[0], bytesAvailable);

    if ((inference.buf_ready == 0) && (record_ready == true)) {
        for(int i = 0; i < bytesRead>>1; i++) {
            inference.buffer[inference.buf_count++] = sampleBuffer[i];

            if(inference.buf_count >= inference.n_samples) {
                inference.buf_count = 0;
                inference.buf_ready = 1;
                break;
            }
        }
    }
}

/**
 * @brief      Init inferencing struct and setup/start PDM
 *
 * @param[in]  n_samples  The n samples
 *
 * @return     { description_of_the_return_value }
 */
static bool microphone_inference_start(uint32_t n_samples)
{
    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));

    if(inference.buffer == NULL) {
        return false;
    }

    inference.buf_count  = 0;
    inference.n_samples  = n_samples;
    inference.buf_ready  = 0;

    // configure the data receive callback
    PDM.onReceive(&pdm_data_ready_inference_callback);

    // optionally set the gain, defaults to 24
    // Note: values >=52 not supported
    //PDM.setGain(40);

    PDM.setBufferSize(2048);

    // initialize PDM with:
    // - one channel (mono mode)
    if (!PDM.begin(1, EI_CLASSIFIER_FREQUENCY)) {
        ei_printf("ERR: Failed to start PDM!");
        microphone_inference_end();
        return false;
    }

    return true;
}

/**
 * @brief      Wait on new data
 *
 * @return     True when finished
 */
static bool microphone_inference_record(void)
{
    bool ret = true;


    record_ready = true;
    while (inference.buf_ready == 0) {
        delay(10);
    }

    inference.buf_ready = 0;
    record_ready = false;

    return ret;
}

/**
 * Get raw audio signal data
 */
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr)
{
    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);

    return 0;
}

/**
 * @brief      Stop PDM and release buffers
 */
static void microphone_inference_end(void)
{
    PDM.end();
    ei_free(inference.buffer);
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for current sensor."
#endif
