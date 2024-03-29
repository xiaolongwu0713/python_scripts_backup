import random

from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import Dataset, DataLoader
from config import *
import os
import numpy as np
import scipy.io
import re
import matplotlib.pyplot as plt
from scipy.ndimage.interpolation import shift

## usage: aa=loadData(31,1,'good'/'bad'/'power'/'epoch61'), then load the data part by checking aa.keys()
def loadData(pn, session, *args):
    arg=args[0]
    if len(args)==0:
        filename = os.path.join(raw_data,'P'+str(pn), '1_Raw_Data_Transfer',
                                'P'+str(pn)+'_H'+str(mode)+'_'+str(session)+'_Raw.mat')
    else:
        if arg=='good':
            filename=os.path.join(processed_data,'P'+str(pn),
                                  'P'+str(pn)+'_H'+str(mode)+'_'+str(session)+'_goodLineChn.mat')
        elif arg=='bad':
            filename = os.path.join(processed_data, 'P' + str(pn),
                                    'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_goodLineChn.mat')
        elif arg == 'discard':
            filename = os.path.join(processed_data, 'P' + str(pn),
                                'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_discardChn.mat')
        elif arg == 'power':
            filename = os.path.join(processed_data, 'P' + str(pn),
                                'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_power.mat')
        elif arg == 'events':
            filename = os.path.join(processed_data, 'P' + str(pn),'eeglabData',
                                'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_eventtable.txt')
            tmp=a=np.loadtxt(filename)
            return tmp
        elif arg == 'eventave':
            filename = os.path.join(processed_data, 'P' + str(pn),'eeglabData',
                                'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_eventtable_ave.mat')
        elif arg == 'eventave':
            filename = os.path.join(processed_data, 'P' + str(pn),'eeglabData',
                                'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_eventtable_ave.mat')
        elif re.compile('epoch').match(arg):
            filename=os.path.join(processed_data, 'P' + str(pn),'eeglabData',
                                'P' + str(pn) + '_H' + str(mode) + '_' + str(session) + '_' + arg+'.mat')
    mat = scipy.io.loadmat(filename)
    return mat  # return np arrary. avedata is the key of this dict, data dim: eles,time,trials

def add_arrows(axes):
    # add some arrows at 60 Hz and its harmonics
    for ax in axes:
        freqs = ax.lines[-1].get_xdata()
        psds = ax.lines[-1].get_ydata()
        for freq in (60, 120, 180, 240):
            idx = np.searchsorted(freqs, freq)
            # get ymax of a small region around the freq. of interest
            y = psds[(idx - 4):(idx + 5)].max()
            ax.arrow(x=freqs[idx], y=y + 18, dx=0, dy=-12, color='red',
                     width=0.1, head_width=3, length_includes_head=True)

def read_rawdata():
    datafile1 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move1TrainRawData.mat'
    datafile11 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move1TestRawData.mat'
    datafile2 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move2TrainRawData.mat'
    datafile21 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move2TestRawData.mat'
    datafile3 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move3TrainRawData.mat'
    datafile31 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move3TestRawData.mat'
    datafile4 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move4TrainRawData.mat'
    datafile41 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move4TestRawData.mat'
    data1 = scipy.io.loadmat(datafile1)
    data11 = scipy.io.loadmat(datafile11)
    data2 = scipy.io.loadmat(datafile2)
    data21 = scipy.io.loadmat(datafile21)
    data3 = scipy.io.loadmat(datafile3)
    data31 = scipy.io.loadmat(datafile31)
    data4 = scipy.io.loadmat(datafile4)
    data41 = scipy.io.loadmat(datafile41)

    traintmp1 = data1['train']
    traintmp11= data11['test']
    traintmp2 = data2['train']
    traintmp21 = data21['test']
    traintmp3 = data3['train']
    traintmp31 = data31['test']
    traintmp4 = data4['train']
    traintmp41 = data41['test']

    dataset=np.concatenate((traintmp1,traintmp11,traintmp2,traintmp21,traintmp3,traintmp31,traintmp4,traintmp41),axis=0) # (2010000, 20)

    # fs=1000, get 5 test period.
    testx=np.transpose(dataset[-75000:,:-1]) #(114, 1500)
    testy=np.transpose(dataset[-75000:,-1]) # (1500,)
    trainx=np.transpose(dataset[0:-75000,:-1]) #  (114, 38692)
    trainy=np.transpose(dataset[:-75000,-1]) # (38692,)

    del data1,data11,data2,data21,data3,data31,data4,data41
    del traintmp1, traintmp11,traintmp2,traintmp21,traintmp3,traintmp31,traintmp4,traintmp41

    return trainx,trainy,testx, testy


def read_fbanddata():
    datafile1 = '/Users/long/BCI/matlab_scripts/force/data/SEEG_Data/move1TrainData3D.mat'
    datafile2 = '/Users/long/BCI/matlab_scripts/force/data/SEEG_Data/move2TrainData3D.mat'
    datafile3 = '/Users/long/BCI/matlab_scripts/force/data/SEEG_Data/move3TrainData3D.mat'
    datafile4 = '/Users/long/BCI/matlab_scripts/force/data/SEEG_Data/move4TrainData3D.mat'
    data1 = scipy.io.loadmat(datafile1)
    #data2 = scipy.io.loadmat(datafile2)
    data3 = scipy.io.loadmat(datafile3)
    data4 = scipy.io.loadmat(datafile4)

    traintmp1 = data1['train'] #(182, 299, 36)
    #traintmp2 = data2['train']
    traintmp3 = data3['train'] #(182, 299, 30)
    traintmp4 = data4['train'] #(182, 299, 38)

    testNum=2
    train=np.concatenate((traintmp1[:,:,:-testNum],traintmp3[:,:,:-testNum],traintmp4[:,:,:-testNum]),axis=2) # (182, 299, 98)
    test = np.concatenate((traintmp1[:, :, -testNum:], traintmp3[:, :, -testNum:], traintmp4[:, :, -testNum:]), axis=2) #(182, 299, 6)

    trainx=train[:-2,:,:] #(180, 299, 98)
    trainy=train[180,:,:] #(299, 98)

    testx=test[:-2,:,:] #(180, 299, 6)
    testy=test[180,:,:] #(299, 6)

    return trainx,trainy,testx, testy

def plotloss(ax,trainlose,testlost):
    with open(trainlose) as f:
        trainlose = f.read().splitlines()
    with open(testlost) as f:
        testlose = f.read().splitlines()
    x=len(testlose)
    trainlose=[float(x) for x in trainlose]
    testlose = [float(x) for x in testlose]
    plt.cla()
    ax.plot(testlose, label='test lose')
    ax.plot(trainlose, label='train lose')
    plt.legend()
    plt.show()
    plt.pause(2)
    plt.savefig('trainAndTestLoseCurve.png')

# system will hang if read all four movement raw data as one 3D.
#TODO: not working, data too big when depth=500, system hang
def read_rawdataAs3D(depth=500,prediction=1):
    datafile1 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move1TrainRawData.mat'
    datafile11 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move1TestRawData.mat'
    datafile2 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move2TrainRawData.mat'
    datafile21 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move2TestRawData.mat'
    datafile3 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move3TrainRawData.mat'
    datafile31 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move3TestRawData.mat'
    datafile4 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move4TrainRawData.mat'
    datafile41 = '/Users/long/Documents/BCI/matlab_scripts/force/pls/move4TestRawData.mat'
    data1 = scipy.io.loadmat(datafile1)
    data11 = scipy.io.loadmat(datafile11)
    data2 = scipy.io.loadmat(datafile2)
    data21 = scipy.io.loadmat(datafile21)
    data3 = scipy.io.loadmat(datafile3)
    data31 = scipy.io.loadmat(datafile31)
    data4 = scipy.io.loadmat(datafile4)
    data41 = scipy.io.loadmat(datafile41)

    traintmp1 = data1['train']
    traintmp11= data11['test']
    traintmp2 = data2['train']
    traintmp21 = data21['test']
    traintmp3 = data3['train']
    traintmp31 = data31['test']
    traintmp4 = data4['train']
    traintmp41 = data41['test']
    #dataset=np.concatenate((traintmp1,traintmp11,traintmp2,traintmp21,traintmp3,traintmp31,traintmp4,traintmp41),axis=0).transpose() # (2010000, 20)
    # still too big:  print("%d bytes" % (ds1.size * ds1.itemsize))
    ds1 = np.concatenate((traintmp1, traintmp11),axis=0).transpose()
    ds2 = np.concatenate((traintmp2, traintmp21), axis=0).transpose()
    ds3 = np.concatenate((traintmp3, traintmp31), axis=0).transpose()
    ds4 = np.concatenate((traintmp4, traintmp41), axis=0).transpose()

    trainx1 = np.zeros((depth,ds1.shape[0]-1,ds1.shape[1]-depth+1)) # (depth, feature, time)
    trainy1 = np.zeros((ds1.shape[1], 1))

    tmpdataset = ds1[:19, :]
    for i in range(depth):
        trainx1[i,:,:]=tmpdataset[:,i:-(depth-i-1)]
    pass
    #return trainx,trainy,testx, testy

def rawData():
    activeChannels = [8, 9, 10, 18, 19, 20, 21, 22, 23, 24, 62, 63, 69, 70, 105, 107, 108, 109, 110,111] # 111 is force channel
    badtrial1 = [12, 13, 21, 22, 23, 24, 26]
    badtrial2 = [23, 24, 28]
    badtrial3 = [3, 4, 8, 11, 16, 21, 22, 23, 24, 25, 29]
    badtrial4 = [4, 21, 24, 25, 29]
    badtrials={}

    badtrials['1'] = np.array(badtrial1) - 1
    badtrials['2'] = np.array(badtrial2) - 1
    badtrials['3'] = np.array(badtrial3) - 1
    badtrials['4'] = np.array(badtrial4) - 1

    activeChannels=np.array(activeChannels)-1
    datafile1 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move1.mat'
    datafile2 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move2.mat'
    datafile3 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move3.mat'
    datafile4 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move4.mat'
    data1 = scipy.io.loadmat(datafile1)
    data2 = scipy.io.loadmat(datafile2)
    data3 = scipy.io.loadmat(datafile3)
    data4 = scipy.io.loadmat(datafile4)
    data1 = data1['data'] # (channel, time, trials)
    data2 = data2['data']
    data3 = data3['data']
    data4 = data4['data']
    data = {}
    data['1'] = np.float32(data1)
    data['2'] = np.float32(data2)
    data['3'] = np.float32(data3)
    data['4'] = np.float32(data4)

    for i in range(4):
        move=str(int(float(i)) + 1)
        alltrialidx = range(data[move].shape[2])  # 0--39
        trialidx = np.setdiff1d(alltrialidx, badtrials[str(int(float(i)) + 1)])
        data[move] = data[move][activeChannels, :, :]
        data[move] = data[move][:, :, trialidx]  # (channels, time,trials), (20, 15000, 33) # last channel is force
    return data

#import grasp.utils as utils
#aa=utils.rawData()
#np.save('/Users/long/Documents/BCI/python_scripts/grasp/data/rawdata.npy', aa)

# a smaller set, few trials
def rawDataSmaller(trialnum=30):
    wholedata=np.load('/Users/long/Documents/BCI/python_scripts/grasp/data/rawdata.npy',allow_pickle='TRUE').item()
    wholedata1=np.concatenate((wholedata['1'],wholedata['2'],wholedata['3']),axis=2) # 3 movement data (20, 15000, 99)
    idx=list(range(99))
    randtrial=random.sample(idx,trialnum)
    left = list(np.setdiff1d(idx, randtrial))
    pickone=random.sample(left,1)
    train=wholedata1[:,:,randtrial] #(20, 15000, 30)
    test=wholedata1[:,:,pickone] #(20, 15000, 2)
    return train,test

# save each 15s movement is a 3D cube to disk
def preprocess():
    data=rawData()
    chns = 19
    depth = 500  # 500 ms
    predict = 1  # predict next point
    print('lala')
    for k, (movetype,movedata) in enumerate(data.items()):
        if k==0:
            # iterate every single trial
            triallen = movedata.shape[1]
            trialnum=movedata.shape[2]
            len = triallen - depth  # 14500
            trainx = np.zeros((chns, len, depth))  # (19, 14500, 500)
            # put all trials force in one array
            trainy=np.zeros((len,trialnum.shape[0])) # len * trialNumber

            for trial in range(trialnum):
                print('processing ' + str(movetype) + ' , trial:' + str(trial + 1))
                force=movedata[-1,:,trial] # foce data
                trialdata=movedata[:-1,:,trial] #(15000, 19)
                trainy[:,trial]=force[500:] # (14500,)
                for i in range(depth):
                    #print(i)
                    if i==(depth-1):
                        trainx[:, :, i] = trialdata[:, i:-1]
                    else:
                        trainx[:,:,i] = trialdata[:, i:-(depth - i)]
                filename='/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/dataloader/move'+str(movetype)+'Trial'+str(trial)
                np.save(filename, trainx)
            filename = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/dataloader/force' + str(movetype)
            print('save force data.')
            np.save(filename, trainy.transpose())
#forcefile='/Users/long/BCI/matlab_scripts/force/data/SEEG_Data/dataloader/train/force1.npy'
#force=np.load(forcefile)

# iter 3D 15s data from disk
class itermove(Dataset):
    def __init__(self, root_dir='/Users/long/BCI/matlab_scripts/force/data/SEEG_Data/dataloader/train', movetype=1):
        self.root_dir = root_dir
        self.movetype = movetype
        self.force=np.load(os.path.join(self.root_dir,'force'+str(movetype)+'.npy')) # (time14500,trials36)

    def __len__(self):
        return self.force.shape[1]

    def __getitem__(self, idx):
        movedatafile = os.path.join(self.root_dir,'move'+str(self.movetype)+'Trial'+str(idx)+'.npy')
        movedata=np.load(movedatafile)
        force = self.force[:,idx]
        data = { 'data': movedata, 'force': force}
        return data


def read_rawdata_3D(fullOrTruncate,realOrTarget):
    activeChannels = np.asarray([8, 9, 10, 18, 19, 20, 21, 22, 23, 24, 62, 63, 69, 70, 105, 107, 108, 109, 110])-1
    alltrials=np.arange(40)
    badtrial1=np.asarray([22, 23, 24, 26]);  badtrial1=badtrial1-1
    badtrial2= np.asarray([23, 24, 28]); badtrial2=badtrial2-1
    badtrial3= np.asarray([4, 8, 11, 16, 21,22,23,24,25, 29]); badtrial3=badtrial3-1
    badtrial4= np.asarray([24, 29]); badtrial4=badtrial4-1
    goodtrial1 = np.setdiff1d(alltrials, badtrial1)
    goodtrial2 = np.setdiff1d(alltrials, badtrial2)
    goodtrial3 = np.setdiff1d(alltrials, badtrial3)
    goodtrial4 = np.setdiff1d(alltrials, badtrial4)

    datafile1 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move1.mat'
    datafile2 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move2.mat'
    datafile3 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move3.mat'
    datafile4 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move4.mat'

    data1 = scipy.io.loadmat(datafile1)
    data2 = scipy.io.loadmat(datafile2)
    data3 = scipy.io.loadmat(datafile3)
    data4 = scipy.io.loadmat(datafile4)

    #(112, 15000, 40)
    datatmp1 = data1['data'][:,:,goodtrial1] #(113, 15000, 36)
    datatmp2 = data2['data'][:,:,goodtrial2] #(113, 15000, 37)
    datatmp3 = data3['data'][:,:,goodtrial3] #(113, 15000, 30)
    datatmp4 = data4['data'][:,:,goodtrial4] #(113, 15000, 38)
    dataset=np.concatenate((datatmp1,datatmp2,datatmp3,datatmp4),axis=2) # (112, 15000, 104)

    scaler = MinMaxScaler(feature_range=(-1, 1))
    #for trial in range(dataset.shape[2]):
    #    dataset[:,:,trial] = np.transpose(scaler.fit_transform(np.transpose(dataset[:,:,trial])))

    if fullOrTruncate=='truncate':
        dataset=dataset[:,0:10000,:] # only regress to early 10s
    elif fullOrTruncate=='full':
        pass
    else:
        print('full or truncate')
        return 1
    del data1,data3,data4,datatmp1,datatmp3,datatmp4
    index=np.arange(dataset.shape[2])
    picktest=[20,21,40,41,80,81,120,121]
    picktrain = np.setdiff1d(index, picktest)

    if realOrTarget=='real':
        extraChannel=110
    elif realOrTarget=='target':
        extraChannel = 111
    else:
        print ('Predict on which signal: real or target')
        return 1
    channels=np.concatenate((activeChannels,np.asarray([extraChannel,])),axis=0) # 110 is real forct, 111 is target
    trainx = dataset[channels,:,:][:,:,picktrain] #(20, 15000, 94)
    trainy = trainx[-1,:,:] #(15000, 94)
    #trainy=np.reshape(trainy,[1,-1],order='F'), then plot to check data
    trainx=trainx[:-1,:,:] #(19, 15000, 94)

    testx = dataset[channels, :, :][:,:,picktest]  # (109, 15000, 20)
    testy = testx[-1, :, :]  # (15000, 20)
    # testy=np.reshape(testy,[1,-1],order='F'), plt.plot(np.squeeze(testy))
    testx = testx[:-1, :, :]  # (19, 15000, 10)

    return trainx,trainy,testx, testy


# generate 3D data of one trial data on the fly
def gen3DOnTheFly(traindata): # traindata: (20channels, 15000times, trialNum)
    chns = 19
    wind=500
    #for k, (movetype,movedata) in enumerate(traindata.items()):
    trialnum = traindata.shape[2]
    for trial in range(trialnum): # for each single 15s movedata
        tmp=traindata[:,:,trial] # trialdata: 20*15000, movedata:channel*time*trials
        #trialdata=tmp[:-1,:] # 19*15000
        trialdata = tmp[:, :]  # 20*15000  # use history force data
        trainy=tmp[-1,:] # force
        trainy=trainy[wind:]

        T = traindata.shape[1] # T: 15000
        len = T - wind  # 14500
        trainx = np.zeros((chns+1, len, wind))  # (19, 14500, 500)

        for i in range(wind):
            # print(i)
            if i == (wind - 1):
                trainx[:, :, i] = trialdata[:, i:-1]
            else:
                trainx[:, :, i] = trialdata[:, i:-(wind - i)]

        yield trainx, trainy


def readRestForModelTest():
    activeChannels = np.asarray([8, 9, 10, 18, 19, 20, 21, 22, 23, 24, 62, 63, 69, 70, 105, 107, 108, 109, 110])-1
    alltrials=np.arange(40)
    testtrial1=np.asarray([24, 26]);  testtrial1=testtrial1-1
    testtrial2= np.asarray([23, 24]); testtrial2=testtrial2-1
    testtrial3= np.asarray([8,21,29]); testtrial3=testtrial3-1
    testtrial4= np.asarray([24,]); testtrial4=testtrial4-1

    datafile1 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move1.mat'
    #datafile2 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move2.mat'
    datafile3 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move3.mat'
    datafile4 = '/Users/long/Documents/BCI/matlab_scripts/force/data/SEEG_Data/move4.mat'

    data1 = scipy.io.loadmat(datafile1)
    #data2 = scipy.io.loadmat(datafile2)
    data3 = scipy.io.loadmat(datafile3)
    data4 = scipy.io.loadmat(datafile4)

    #(112, 15000, 40)
    datatmp1 = data1['data'][:,:,testtrial1] #(113, 15000, 36)
    #datatmp2 = data2['data'][:,:,goodtrial2] #(113, 15000, 37)
    datatmp3 = data3['data'][:,:,testtrial3] #(113, 15000, 30)
    datatmp4 = data4['data'][:,:,testtrial4] #(113, 15000, 38)
    dataset=np.concatenate((datatmp1,datatmp3,datatmp4),axis=2) # (112, 15000, 104)

    scaler = MinMaxScaler(feature_range=(-1, 1))
    #for trial in range(dataset.shape[2]):
    #    dataset[:,:,trial] = np.transpose(scaler.fit_transform(np.transpose(dataset[:,:,trial])))

    dataset=dataset[:,0:10000,:] # only regress to early 10s
    del data1,data3,data4,datatmp1,datatmp3,datatmp4

    channels=np.concatenate((activeChannels,np.asarray([111,])),axis=0) # 110 is real forct, 111 is target
    testx = dataset[channels,:,:] #(20, 15000, 94)
    testy = testx[-1,:,:] #(15000, 94)
    #trainy=np.reshape(trainy,[1,-1],order='F'), then plot to check data
    testx=testx[:-1,:,:] #(19, 15000, 94)

    return testx,testy
