import torch
import torch.nn as nn
from torch.autograd import Variable
import math

def convtransp_output_shape(h_w, kernel_size=1, stride=1, pad=0,dilation=1):
    """
    Utility function for computing output of transposed convolutions
    takes a tuple of (h,w) and returns a tuple of (h,w)
    """
    if type(h_w) is not tuple:
        h_w = (h_w, h_w)
    if type(kernel_size) is not tuple:
        kernel_size = (kernel_size, kernel_size)
    if type(stride) is not tuple:
        stride = (stride, stride)
    if type(pad) is not tuple:
        pad = (pad, pad)
    if type(dilation) is not tuple:
        dilation = (dilation,dilation)
    h = math.floor((h_w[0] + 2*pad[0] - dilation[0]*(kernel_size[0]-1) - 1) / stride[0] + 1)
    w = math.floor((h_w[1] + 2*pad[1] - dilation[1]*(kernel_size[1]-1) - 1) / stride[1] + 1)
    return h, w

class deepwise_separable_conv(nn.Module):
    def __init__(self,nin,nout,kernelSize):
        super(deepwise_separable_conv,self).__init__()
        self.kernelSize = kernelSize
        self.time_padding = int(kernelSize//2)
        self.depthwise = nn.Conv2d(in_channels=nin,out_channels=nin,kernel_size=(1,kernelSize),
                                   padding=(0,self.time_padding),groups=nin,bias=False)
        self.pointwise = nn.Conv2d(in_channels=nin,out_channels=nout, kernel_size=1,groups=1,bias=False)
    def forward(self, input):
        dw = self.depthwise(input)
        pw = self.pointwise(dw)
        return pw
    def get_output_size(self,h_w):
        return convtransp_output_shape(h_w, kernel_size=(1,self.kernelSize), stride=1, pad=(0,self.time_padding), dilation=1)


class EEGNet_experimental(nn.Module):
    '''Data shape = (trials, kernels, channels, samples), which for the
        input layer, will be (trials, 1, channels, samples).'''
    #TODO resolve problems with avg padding when the end of the epoch lost
    #TODO possible solution via padding or AdaptiveAvgPool2d
    def __init__(self,nb_classes=10, Chans=114, Samples=20,
           dropoutRates=(0.25,0.25), kernLength1=5,kernLength2=5, poolKern1=4,poolKern2=8, F1=4,
           D=2, F2=8, norm_rate=0.25, dropoutType='Dropout'):
        super(EEGNet_experimental,self).__init__()
        self.Chans = Chans
        self.Samples = Samples
        self.output_sizes = {}
        #block1
        time_padding = int((kernLength1//2))
        self.conv1 = nn.Conv2d(in_channels=1,out_channels=F1,kernel_size =(1,kernLength1),padding=(0,time_padding), stride=1,bias=False)
        self.output_sizes['conv1']=convtransp_output_shape((Chans,Samples), kernel_size=(1,kernLength1), stride=1,
                                                           pad=(0,time_padding))
        self.batchnorm1 = nn.BatchNorm2d(num_features=F1, affine=True)
        self.depthwise1 = nn.Conv2d(in_channels=F1,out_channels=F1*D,kernel_size=(Chans,1),groups=F1,padding=0,bias=False)
        self.output_sizes['depthwise1'] = convtransp_output_shape(self.output_sizes['conv1'], kernel_size=(Chans,1),
                                                                  stride=1, pad=0)
        self.batchnorm2 = nn.BatchNorm2d(num_features=F1*D, affine=True)
        self.activation_block1 = nn.ELU()
        # self.avg_pool_block1 = nn.AvgPool2d((1,poolKern1))
        # self.output_sizes['avg_pool_block1'] = convtransp_output_shape(self.output_sizes['depthwise1'], kernel_size=(1, poolKern1),
        #                                                           stride=(1,poolKern1), pad=0)
        #self.avg_pool_block1 = nn.AdaptiveAvgPool2d((1,int(self.output_sizes['depthwise1'][1]/2))) # used to be 4
        self.avg_pool_block1 = nn.AdaptiveAvgPool2d((1, 32))
        self.output_sizes['avg_pool_block1'] = (1,32)
        self.dropout_block1 = nn.Dropout(p=dropoutRates[0])

        #block2
        self.separable_block2 = deepwise_separable_conv(nin=F1*D,nout=F2,kernelSize=kernLength2)
        self.output_sizes['separable_block2'] = self.separable_block2.get_output_size(self.output_sizes['avg_pool_block1'])
        self.activation_block2 = nn.ELU()
        # self.avg_pool_block2 = nn.AvgPool2d((1,poolKern2))
        # self.output_sizes['avg_pool_block2'] = convtransp_output_shape(self.output_sizes['separable_block2'],
        #                                                                kernel_size=(1, poolKern2),
        #                                                                stride=(1, poolKern2), pad=0)
        #self.avg_pool_block2 = nn.AdaptiveAvgPool2d((1,int(self.output_sizes['separable_block2'][1]/4)))
        # self.output_sizes['avg_pool_block2'] = (1,int(self.output_sizes['separable_block2'][1]/4))
        self.avg_pool_block2 = nn.AdaptiveAvgPool2d((1, 10))
        self.output_sizes['avg_pool_block2'] = (1, 10)

        self.dropout_block2 = nn.Dropout(dropoutRates[1])

        self.flatten = nn.Flatten()
        #n_size = self.get_features_dim(Chans,Samples)
        #self.dense = nn.Linear(n_size,nb_classes)

        # block 3
        self.lstm = nn.LSTM(8, 20)
        self.ln1 = nn.Linear(20, 1)
        self.elu1 = nn.ELU(alpha=1.0)
        self.ln2 = nn.Linear(30, 1)
        self.elu2 = nn.ELU(alpha=1.0)

    def get_features_dim(self,Chans,Samples):
        bs = 1
        x = Variable(torch.rand((bs,1,Chans, Samples)))
        output_feat,out_dims = self.forward(x)
        n_size = output_feat.data.view(bs, -1).size(1)
        return n_size

    def forward(self,input):
        out_dims = {}
        block1 = self.conv1(input)
        out_dims['conv1'] = block1.size()
        block1 = self.batchnorm1(block1)
        block1 = self.depthwise1(block1)
        out_dims['depthwise1'] = block1.size()
        block1 = self.batchnorm2(block1)
        block1 = self.activation_block1(block1)
        #block1 = self.avg_pool_block1(block1)
        out_dims['avg_pool_block1'] = block1.size()
        block1 = self.dropout_block1(block1)

        block2 = self.separable_block2(block1)
        out_dims['separable_block2'] = block1.size()
        block2 = self.activation_block2(block2)
        #block2 = self.avg_pool_block2(block2)
        out_dims['avg_pool_block2'] = block1.size()
        block2 = self.dropout_block2(block2)

        block3=torch.squeeze(block2).permute(2,0,1)
        block3 = self.lstm(block3)[0] # output of lstm
        block3=block3[-1].squeeze()
        block3 = self.ln1(block3).squeeze()
        output = self.elu2(block3).squeeze()
        return output

    def weights_init(self):
        def weights_init(m):
            if isinstance(m, nn.Conv2d):
                torch.nn.init.xavier_uniform(m.weight.data)

