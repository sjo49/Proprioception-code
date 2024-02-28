"""
Created on Mon Dec 16 08:14:56 2019

@author: hrist

"""

import numpy as np
from scipy.signal import butter, lfilter

class EMGfilters():
    
    def __init__(self,hp_cutOff,lp_cutOff,env_cutOff,fs,order=5,ch_numb=8):
        #Setting up filter parameters
        self.zil=np.zeros([order,ch_numb])
        self.zie=np.zeros([2,ch_numb])
        self.zih=np.zeros([order,ch_numb])
        self.zibs=np.zeros([4,ch_numb])
        Wn_hp = hp_cutOff*2 / fs
        Wn_lp = lp_cutOff*2 / fs
        Wn_env = env_cutOff*2 / fs
        Wn_bsl = 45*2 / fs
        Wn_bsh = 55*2 / fs
        self.b_hp, self.a_hp = butter(order, Wn_hp, btype='high', analog = False)
        self.b_lp, self.a_lp = butter(order, Wn_lp, btype='low', analog = False)
        self.b_env, self.a_env = butter(2, Wn_env, btype='low', analog = False)
        self.b_bs, self.a_bs = butter(2, [Wn_bsl, Wn_bsh], btype='bandstop', analog = False)
        
    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='bandpass')
        y = lfilter(b, a, data)
        return y
    
    def butter_bandstop_filter(self,data):

        y,self.zibs = lfilter(self.b_bs, self.a_bs, data, axis=0, zi=self.zibs)
        return y
    
    def butter_lowpass_filter(self,data):
        y,self.zil = lfilter(self.b_lp, self.a_lp, data, axis=0, zi=self.zil)
        return y
    
    def butter_lowpassEnv_filter(self,data):
        y,self.zie = lfilter(self.b_env, self.a_env, data, axis=0, zi=self.zie)
        return y
    
    def butter_highpass_filter(self, data):
        y,self.zih = lfilter(self.b_hp, self.a_hp, data, axis=0, zi=self.zih)
        return y
    
    def common_mean_filter(self, data,usedChannels=np.arange(0,8,1)):
            
        emg_cmTemp = np.zeros((np.size(data,axis=0),np.size(data,axis=1)))   
        cmVect = np.ones((1,np.size(data,axis=1)))
        
        sPoints = np.arange(0,data[:,1].size - 24,25)
        ePoints=sPoints+24
        ePoints[-1]=data[:,1].size
        nWindows = len(sPoints)
            
        for j in range(nWindows):
            mean_data = data[sPoints[j]:ePoints[j]+1,usedChannels]
            sum_mean=np.sum(mean_data**2,axis=0)
            chan_order=np.argsort(sum_mean)
            mean_val=np.mean(mean_data[:,chan_order[0:round(len(chan_order)/2)]],axis=1)
            emg_cmTemp[sPoints[j]:ePoints[j]+1,usedChannels] = data[sPoints[j]:ePoints[j]+1,usedChannels] - np.outer(mean_val,cmVect[:,usedChannels])
            
        return emg_cmTemp