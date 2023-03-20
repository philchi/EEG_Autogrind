import pylsl
import collections
import time as t
import numpy as np
import scipy.signal as signal

terminate = False
store_data = False
send_result = False

def createMrkStream(name):
    info = pylsl.stream_info(name, 'Markers', 1, 0, pylsl.cf_string, 'unsampledStream')
    outlet = pylsl.stream_outlet(info, 1, 1)
    return outlet

def lsl_inlet(name):
    inlet = None
    info = pylsl.resolve_stream('name', name)
    print('resolve')
    inlet = pylsl.stream_inlet(info[0], recover=0)
    print('inlet')
    return inlet

# init lsl streams
eegstream = lsl_inlet('phil_EEG')
mrkstream = lsl_inlet('SSVEP_Markers')
results = createMrkStream('egg_res')

print(eegstream)

# init eeg data storage
data = collections.deque()

# init freq bands
bands = {'left': [7, 9], 'up': [9, 11], 'down': [11, 13], 'right': [13, 15]}

# init filter
#b = signal.firwin(numtaps=31, cutoff=[2, 30], pass_zero='bandpass', fs=250.0)
#a = 1
b, a = signal.butter(4, [2, 30], btype='bandpass', fs=250.0)

while not terminate:
    mrk, t_mrk = mrkstream.pull_sample(timeout=0)
    eeg, t_eeg = eegstream.pull_sample(timeout=0)

    if mrk != None:
        if mrk[0] == 'start' and not store_data:
            print('start recording')
            data = collections.deque()
            store_data = True

        elif mrk[0] == 'pause':
            print('stopped recording')
            store_data = False
            send_result = True

        elif mrk[0] == 'die':
            store_data = False
            send_result = False
            terminate = True

    if store_data and eeg != None:
        data.append(eeg)

    elif send_result:
        send_result = False
        # do processing/classification here
        res = 'temp'
        chan1 = [i[0] for i in data]
        
        chan1 = signal.filtfilt(b, a, chan1)
        freqs1, psd1 = signal.periodogram(chan1, 250.0)
        mx1 = freqs1[np.where(psd1==max(psd1))]
        print(mx1)
        
        for k in bands:
            if mx1 >= bands[k][0] and mx1 < bands[k][1]:
                res = k

        '''
        mx_var = 0
        out = 0
        for k in bands:
            #b, a = signal.butter(4, [bands[k][0], bands[k][1]], btype='bandpass', fs=250.0)
            b = signal.firwin(numtaps=31, cutoff=[bands[k][0], bands[k][1]], pass_zero='bandpass', fs=250.0)
            filted = signal.filtfilt(b, a, chan1)
            variance = np.var(filted)
            print(variance)
            if variance > mx_var:
                mx_var = variance
                out = k
        print(out)'''
        
        # Wait 50ms then send a message (to give the task a chance to listen)
        t.sleep(0.05)
        print('Sent command')
        results.push_sample(pylsl.vectorstr([res]))
        