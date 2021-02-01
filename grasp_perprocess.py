from mne.time_frequency import tfr_morlet
from config import *
#from utils import *
import numpy as np
import h5py
import hdf5storage
import mne
import matplotlib.pyplot as plt

# info
n_channels = 73
sampling_rate = 1000

## load channel
seegS1file='/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/PF6_F_1.mat'
triggerS1file='/Users/long/Documents/BCI/matlab_scripts/force/data/Trigger_Data/Trigger_Information_1.mat'
emgS1file='/Users/long/Documents/BCI/matlab_scripts/force/data/HDEMG_Data/SYF_session1.mat'
forceS1file='/Users/long/Documents/BCI/matlab_scripts/force/data/Force_Data/SYF-1-2.mat'

### 1, channel data
mat = hdf5storage.loadmat(seegS1file)
channels=[mat['ChnName'][i][0][0][0] for i in range(len(mat['ChnName']))] #list with len=126
seeg=mat['Data'] # (1296162, 126)
fs=mat['Fs'][0][0] # 2000
# refs=mat['#refs#'] can't read the #refs# data

### 2, trigger data
mat = hdf5storage.loadmat(triggerS1file)
trigger_time=mat['Info']['task_time'][0][0] #np array, shape: (1,40)
trial_len=mat['Info']['trial_length'][0][0] #np array, shape: (1,40)
xaxis=mat['Info']['Xaxis'][0][0] # (1, 40) each element has 4 values
yaxis=mat['Info']['Yaxis'][0][0] # (1, 40) each element has 4 values
movement=mat['Info']['Exp_Seq'][0][0] #(1, 40) movement type

### 3, emg data
mat = hdf5storage.loadmat(emgS1file)
emg=mat['Sig'] # shape: (67, 1254250) ???


### 4, force data
mat= hdf5storage.loadmat(forceS1file)
force=mat['t'] # np.array (6039000, 1) ???



with open(seeg1) as f:
    channels=np.asarray([line.split() for line in f])
ch_names=channels[:,3]
ch_names=np.append(ch_names,['STI 01','STI 02']) # events, emg
ch_types=np.append(np.repeat(np.array('seeg'),71),np.repeat(np.array('stim'),2))

### create info
info = mne.create_info(ch_names=list(ch_names), ch_types=list(ch_types), sfreq=sampling_rate)

## create raw data
raw = mne.io.RawArray(myraw, info)

### events
myevents=loadData(31,1,'events')
event_dict = {'move1': 1, 'move2': 2, 'move3': 3,'move4': 4, 'move5': 5}
# or nme can find event from channels of raw data
events = mne.find_events(raw, stim_channel='STI 01',consecutive=False)
emgevents=mne.find_events(raw, stim_channel='EMG')

## some plot
# plot all events
fig = mne.viz.plot_events(events, sfreq=raw.info['sfreq'],first_samp=raw.first_samp, event_id=event_dict)
fig.subplots_adjust(right=0.7)  # make room for legend

#plot certain type channels
channel_to_plot=np.array([1, 2, 3, 4, 5])
channel_to_plot=np.array([9,])
raw.copy().pick_types(seeg=True, stim=False).plot(events=events,scalings=dict(seeg=100),start=3, duration=6,event_color={1: 'r', 2: 'g', 3: 'b', 4: 'm', 5: 'y'})

## extract and evaluate data from raw
sampling_freq = raw.info['sfreq']
start_stop_seconds = np.array([11, 13])
start_sample, stop_sample = (start_stop_seconds * sampling_freq).astype(int)
channel_index = 72
raw_selection = raw[channel_index, start_sample:stop_sample]
x = raw_selection[1]
y = raw_selection[0].T
plt.plot(x, y)

## frequency analysis
# PSD: power spectral density
fig = raw.plot_psd(tmax=np.inf, fmax=250, average=True)

## notch filter
chn = mne.pick_types(raw.info, seeg=True)
freqs = (50, 100, 150, 200)
raw_notch = raw.copy().notch_filter(freqs=freqs, picks=chn)
for title, data in zip(['Un', 'Notch '], [raw, raw_notch]):
    fig = data.plot_psd(fmax=250, average=True)
    fig.subplots_adjust(top=0.85)
    fig.suptitle('{}filtered'.format(title), size='xx-large', weight='bold')
    #add_arrows(fig.axes[:2])

## epoch
epochs = mne.Epochs(raw, events, tmin=-1, tmax=4.5, event_id=event_dict,preload=True)
epochs[0].plot(n_epochs=10,scalings=dict(seeg=100))
epochs['move3'].plot(n_epochs=10,scalings=dict(seeg=100))
# crop epoch
shorter_epochs = epochs.copy().crop(tmin=-1, tmax=4, include_tmax=True)

## visuallization
epochs['move1'].plot_image(picks='seeg', combine='mean')

## frequency analysis
# define frequencies of interest (log-spaced)
freqs = np.logspace(*np.log10([55, 150]), num=80)
n_cycles = freqs / 2.  # different number of cycle per frequency
power= tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles, use_fft=True,return_itc=False, decim=3, n_jobs=1)
chn=15
power.plot([chn], baseline=(-0.5, 0), mode='logratio', title=power.ch_names[chn])

# plot all power on one figure
fig,axes=plt.subplots(ncols=5,nrows=5,figsize=(10,10),)
for chn in np.arange(0,24):
    row=chn//5
    power.plot([chn], baseline=(-0.5, 0), mode='logratio', title=power.ch_names[chn], axes=axes[row][chn-(row)*5])
#### plot power of certain frequency range on channel-vs-time plot

############ BCI Competition III dataset 1 ##############
n_channels = 64
sampling_rate = 1000
filename='/Users/long/BCI/BCI-competition/Competition_train.mat'
mat = scipy.io.loadmat(filename)
samples=mat['X'] #(278, 64, 3000)
targets=mat['Y'] #(278, 1)
x=np.arange(0,samples.shape[2])
trial0chn0=samples[0,0,:]
trial1chn0=samples[1,0,:]
fig=plt.figure()
plt.subplot(211)
plt.plot(x,trial0chn0)
plt.subplot(212)
plt.plot(x,trial1chn0)
plt.show()

ch_names=['channel'+str(i) for i in range(n_channels)]
ch_types=['ecog'] * 64
### create info
info = mne.create_info(ch_names=list(ch_names), ch_types=list(ch_types), sfreq=sampling_rate)

## create raw data
myraw=samples.transpose(1,0,2)
myraw=myraw.reshape(64,3000*278)
raw = mne.io.RawArray(myraw, info)
raw.copy().pick_types(seeg=True, stim=False).plot(events=events,scalings=dict(seeg=100),start=3, duration=6,event_color={1: 'r', 2: 'g', 3: 'b', 4: 'm', 5: 'y'})
fig2=plt.figure()
raw.copy().pick_channels(['channel0',]).plot(duration=3,scalings=dict(ecog=100)) # cant change the duration of plotting??

