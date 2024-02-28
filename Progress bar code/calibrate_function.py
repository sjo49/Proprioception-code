import time
import EMGsqPlusClass as EMGdev
import EMGfiltersCONFIDENTIAL as EMGfilt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import keyboard
import PySimpleGUI as sg



def calibrate(emg: EMGdev):

    #Setting up EMG and Filtering parameters
    emgMode = 1
    chanNumb = 8
    windowSize = 200 #in datapoints
    fs = 2000 #sampling frequency
    lowcut = 20 
    highcut = 500
    envelopecut = 2
    emg_data=np.zeros((windowSize,chanNumb+4))
    emg_filters = EMGfilt.EMGfilters(lowcut,highcut,envelopecut,fs,ch_numb=chanNumb)
    # emg=EMGdev.Sessantaquattro(mode=emgMode,nch=0, )

    #Connect to EMG
    

    #loops for x seconds throughout which EMG data is read, converted to float, and filtered
    loopTime = 10
    time_unit = 0
    time_limit = (loopTime*(fs/windowSize))


    max_val_1 = 0
    max_val_2 = 0
    min_val_1 = 2000
    min_val_2 = 2000


    print("Get ready to relax in...")
    time.sleep(2)
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)

    i = 0

    while time_unit < time_limit:
        #EMG data collection and filtering
        emg_data,bin_data=emg.read_emg()
        emg_float = emg_data[:,0:8].astype(float)

        emg_hp=emg_filters.butter_highpass_filter(emg_float)
        emg_lp=emg_filters.butter_lowpass_filter(emg_hp)
        emg_bs=emg_filters.butter_bandstop_filter(emg_lp)
        emg_abs = np.abs(emg_bs)
        emg_env=emg_filters.butter_lowpassEnv_filter(emg_abs)

        emg_filt_1 = emg_env[:,0]
        emg_val = np.max(emg_filt_1)

        emg_filt_2 = emg_env[:,1]
        emg_val_2 = np.max(emg_filt_2)

        if emg_val_2 > 0 and emg_val_2 < min_val_2: 
            min_val_2 = emg_val_2

        if emg_val > 0 and emg_val < min_val_1: 
            min_val_1 = emg_val

        if  i % 5 == 0:
            print(emg_val_2)

        i += 5

        #Thumb will be stopped when q is pressed
        if keyboard.is_pressed('q'):
            print("END")
            break

        time_unit +=1

    time_unit  = 0
    print("Get ready to contract...")
    time.sleep(2)
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    time.sleep(1)

    while time_unit < time_limit:

        #EMG data collection and filtering
        emg_data,bin_data=emg.read_emg()
        emg_float = emg_data[:,0:8].astype(float)

        emg_hp=emg_filters.butter_highpass_filter(emg_float)
        emg_lp=emg_filters.butter_lowpass_filter(emg_hp)
        emg_bs=emg_filters.butter_bandstop_filter(emg_lp)
        emg_abs = np.abs(emg_bs)
        emg_env=emg_filters.butter_lowpassEnv_filter(emg_abs)

        emg_filt_1 = emg_env[:,0]
        emg_val = np.max(emg_filt_1)
        if emg_val < 5000 and emg_val > max_val_1:
            max_val_1 = emg_val

        emg_filt_2 = emg_env[:,1]
        emg_val_2 = np.max(emg_filt_2)
        if emg_val_2 < 5000 and emg_val_2 > max_val_2:
            max_val_2 = emg_val_2

        if  i % 5 == 0:
            print(emg_val_2)

        i += 5

        #Thumb will be stopped when q is pressed
        if keyboard.is_pressed('q'):
            print("END")
            break

        time_unit +=1

    cal_1 = max_val_1*0.6
    cal_2 = max_val_2*0.6
    min_cal_1 = min_val_1
    min_cal_2 = min_val_2

    print("STOP")
    print("max_val = ", round(cal_1))
    print("max_val_2 = ",round(cal_2))
    print("min_val = ", round(min_cal_1))
    print("min_val_2 = ",round(min_cal_2))

    #Disconnect the EMG device after the for-loop has finished   

    return cal_1, cal_2, min_cal_1, min_cal_2
