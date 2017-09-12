#!/usr/bin/python

import numpy as np
from random import shuffle

###############################################################################################################################

def shuffle_data(ndata,sel,rdm,fractrain):

    if rdm == 0:
        trrangemax = np.asarray(range(sel[0],sel[1]),int)
    else:
        data_list = range(ndata)
        shuffle(data_list)
        trrangemax = np.asarray(data_list[:rdm],int).copy()
    terange = np.setdiff1d(range(ndata),trrangemax)

    ns = len(terange)
    ntmax = len(trrangemax)
    nt = int(fractrain*ntmax)
    trrange = trrangemax[0:nt]

    return [ns,nt,ntmax,trrange,terange]

###############################################################################################################################

def unflatten_kernel(ndata,size,kernel_flatten):
    # Unpack kernel into the desired format for the code
    kernel = np.zeros((ndata,ndata,size,size),dtype=float)
    k=0
    for i in xrange(ndata):
        for j in xrange(ndata):
            for iim in xrange(size):
                for jjm in xrange(size):
                    kernel[i,j,iim,jjm] = kernel_flatten[k]
                    k += 1

    return kernel

###############################################################################################################################

def unflatten_kernel0(ndata,kernel_flatten):
    # Unpack kernel into the desired format for the code
    kernel = np.zeros((ndata,ndata),dtype=float)
    k=0
    for i in xrange(ndata):
        for j in xrange(ndata):
            kernel[i,j] = kernel_flatten[k]
            k += 1

    return kernel

###############################################################################################################################
