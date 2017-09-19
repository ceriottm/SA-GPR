#!/usr/bin/python

import sys
import numpy as np
import math
import scipy.linalg
import argparse 
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import utils.kern_utils

###############################################################################################################################

def do_sagpr2(lm,fractrain,tens,kernel_flatten,sel,rdm):

    # initialize regression
#    intrins_dev0 = 0.0
#    abs_error0 = 0.0
#    intrins_dev2 = 0.0
#    abs_error2 = 0.0
    ncycles = 1

    lvals = [0,2]
    degen = [(2*l+1) for l in lvals]
    intrins_dev   = np.zeros(len(lvals),dtype=float)
    intrins_error = np.zeros(len(lvals),dtype=float)
    abs_error     = np.zeros(len(lvals),dtype=float)

    #TODO: The input arguments should be changed here.
#    lm = [lm0,lm2]
#    kernel_flatten = [kernel0_flatten,kernel2_flatten]

    print "Results averaged over "+str(ncycles)+" cycles"

    for ic in range(ncycles):

        ndata = len(tens)
        [ns,nt,ntmax,trrange,terange] = utils.kern_utils.shuffle_data(ndata,sel,rdm,fractrain)
       
        # Build kernel matrices.
#        kernel0 = utils.kern_utils.unflatten_kernel0(ndata,kernel0_flatten)
#        kernel2 = utils.kern_utils.unflatten_kernel(ndata,5,kernel2_flatten)
        kernel = [utils.kern_utils.unflatten_kernel(ndata,degen[i],kernel_flatten[i]) for i in xrange(len(lvals))]

        # Partition properties and kernel for training and testing
#        [vtrain,vtest,[k0tr,k2tr],[k0te,k2te]] = utils.kern_utils.partition_kernels_properties(alps,[kernel0,kernel2],trrange,terange)
        [vtrain,vtest,ktr,kte] = utils.kern_utils.partition_kernels_properties(tens,kernel,trrange,terange)

        # Extract the 6 non-equivalent components xx,xy,xz,yy,yz,zz; include degeneracy.
        [tenstrain,tenstest,mask1,mask2] = utils.kern_utils.get_non_equivalent_components(vtrain,vtest)
   
        # Unitary transormation matrix from Cartesian to spherical (l=0,m=0 | l=2,m=-2,-1,0,+1,+2), Condon-Shortley convention.
        CS = np.array([[-1.0/np.sqrt(3.0),0.5,0.0,-1.0/np.sqrt(6.0),0.0,0.5],[0.0,-0.5j,0.0,0.0,0.0,0.5j],[0.0,0.0,0.5,0.0,-0.5,0.0],[-1.0/np.sqrt(3.0),-0.5,0.0,-1.0/np.sqrt(6.0),0.0,-0.5],[0.0,0.0,-0.5j,0.0,-0.5j,0.0],[-1.0/np.sqrt(3.0),0.0,0.0,2.0/np.sqrt(6.0),0.0,0.0]],dtype = complex)
        for i in xrange(6):
            CS[i] = CS[i] * mask1[i]

        # Transformation matrix from complex to real spherical harmonics (l=2,m=-2,-1,0,+1,+2).
#        [CR0,CR2] = utils.kern_utils.complex_to_real_transformation([1,5])
        CR = utils.kern_utils.complex_to_real_transformation(degen)

        # Extract the real spherical components (l=0,l=2) of the polarizabilities.
#        [ [vtrain0,vtrain2],[vtest0,vtest2] ] = utils.kern_utils.partition_spherical_components(alptrain,alptest,CS,[CR0,CR2],[1,5],ns,nt)
#        [ [vtrain0,vtrain2],[vtest0,vtest2] ] = utils.kern_utils.partition_spherical_components(alptrain,alptest,CS,CR,degen,ns,nt)
        [ vtrain_part,vtest_part ] = utils.kern_utils.partition_spherical_components(tenstrain,tenstest,CS,CR,degen,ns,nt)

        meantrain = np.zeros(len(degen),dtype=float)
        for i in xrange(len(degen)):
            if degen[i]==1:
                vtrain_part[i]  = np.real(vtrain_part[i]).astype(float)
                meantrain[i]    = np.mean(vtrain_part[i])
                vtrain_part[i] -= meantrain[i]
                vtest_part[i]   = np.real(vtest_part[i]).astype(float)

#        vtrain0    = np.real(vtrain0).astype(float)
#        meantrain0 = np.mean(vtrain0)
#        vtrain0   -= meantrain0        
#        vtest0     = np.real(vtest0).astype(float)

        # Build training kernels.
#        ktrain0 = np.real(k0tr) + lm0*np.identity(nt)
#        [ktrain0,ktrainpred0] = utils.kern_utils.build_training_kernel(nt,1,k0tr,lm0)
#        [ktrain2,ktrainpred2] = utils.kern_utils.build_training_kernel(nt,5,k2tr,lm2)
#        [ktrain0,ktrainpred0] = utils.kern_utils.build_training_kernel(nt,degen[0],ktr[0],lm[0])
#        [ktrain2,ktrainpred2] = utils.kern_utils.build_training_kernel(nt,degen[1],ktr[1],lm[1])
        ktrain_all_pred = [utils.kern_utils.build_training_kernel(nt,degen[i],ktr[i],lm[i]) for i in xrange(len(degen))]
        ktrain     = [ktrain_all_pred[i][0] for i in xrange(len(degen))]
        ktrainpred = [ktrain_all_pred[i][1] for i in xrange(len(degen))]
    
        # Invert training kernels.
#        invktrvec0 = scipy.linalg.solve(ktrain0,vtrain0)
#        invktrvec2 = scipy.linalg.solve(ktrain2,vtrain2)
#        [invktrvec0,invktrvec2] = [scipy.linalg.solve(ktrain0,vtrain0),scipy.linalg.solve(ktrain2,vtrain2)]
#        invktrvec = [scipy.linalg.solve(ktrain0,vtrain_part[0]),scipy.linalg.solve(ktrain2,vtrain_part[1])]
        invktrvec = [scipy.linalg.solve(ktrain[i],vtrain_part[i]) for i in xrange(len(degen))]

        # Build testing kernels.
#        ktest0 = np.real(k0te)
#        ktest0 = utils.kern_utils.build_testing_kernel(ns,nt,1,k0te)
#        ktest2 = utils.kern_utils.build_testing_kernel(ns,nt,5,k2te)
#        [ktest0,ktest2] = [utils.kern_utils.build_testing_kernel(ns,nt,degen[0],k0te),utils.kern_utils.build_testing_kernel(ns,nt,degen[1],k2te)]
#        ktest = [utils.kern_utils.build_testing_kernel(ns,nt,1,k0te),utils.kern_utils.build_testing_kernel(ns,nt,5,k2te)]
        ktest = [utils.kern_utils.build_testing_kernel(ns,nt,degen[i],kte[i]) for i in xrange(len(degen))]


        # Predict on test data set.
#        outvec0 = np.dot(ktest0,invktrvec0)
#        outvec2 = np.dot(ktest2,invktrvec2)
#        outvec0 += meantrain0
#        outvec0 = np.dot(ktest[0],invktrvec[0])
#        outvec2 = np.dot(ktest[1],invktrvec[1])
#        outvec0 += meantrain[0]

        outvec = [np.dot(ktest[i],invktrvec[i]) for i in xrange(len(degen))]
        for i in xrange(len(degen)):
            if degen[i]==1:
                outvec[i] += meantrain[i]

        # Accumulate errors.
#        intrins_dev0 += np.std(vtest0)**2
#        abs_error0 += np.sum((outvec0-vtest0)**2)/(ns) 

#        intrins_dev2 += np.std(vtest2)**2
#        abs_error2 += np.sum((outvec2-vtest2)**2)/(5*ns)
#        intrins_dev[0] += np.std(vtest_part[0])**2
#        abs_error[0] += np.sum((outvec[0]-vtest_part[0])**2)/(degen[0]*ns) 

#        intrins_dev[1] += np.std(vtest_part[1])**2
#        abs_error[1] += np.sum((outvec[1]-vtest_part[1])**2)/(degen[1]*ns)

        for i in xrange(len(degen)):
            intrins_dev[i] += np.std(vtest_part[i])**2
            abs_error[i] += np.sum((outvec[i]-vtest_part[i])**2)/(degen[i]*ns)

        # Convert the predicted full tensor back to Cartesian coordinates.
#        predcart = utils.kern_utils.spherical_to_cartesian([outvec0,outvec2],[1,5],ns,[CR0,CR2],CS,mask1,mask2)
#        predcart = utils.kern_utils.spherical_to_cartesian([outvec0,outvec2],degen,ns,CR,CS,mask1,mask2)
        predcart = utils.kern_utils.spherical_to_cartesian(outvec,degen,ns,CR,CS,mask1,mask2)

        testcart = np.real(np.concatenate(vtest)).astype(float)

#    intrins_dev[0] = np.sqrt(intrins_dev[0]/float(ncycles))
#    abs_error[0] = np.sqrt(abs_error[0]/float(ncycles))
#    intrins_error[0] = 100*np.sqrt(abs_error[0]**2/intrins_dev[0]**2)
#
#    intrins_dev[1] = np.sqrt(intrins_dev[1]/float(ncycles))
#    abs_error[1] = np.sqrt(abs_error[1]/float(ncycles))
#    intrins_error[1] = 100*np.sqrt(abs_error[1]**2/intrins_dev[1]**2)

    for i in xrange(len(degen)):
        intrins_dev[i] = np.sqrt(intrins_dev[i]/float(ncycles))
        abs_error[i] = np.sqrt(abs_error[i]/float(ncycles))
        intrins_error[i] = 100*np.sqrt(abs_error[i]**2/intrins_dev[i]**2)

    print ""
    print "testing data points: ", ns
    print "training data points: ", nt
#    print "Results for lambda_1 and lambda_3 = ", lm[0], lm[1]
    for i in xrange(len(degen)):
        print "--------------------------------"
        print "RESULTS FOR L=%i MODULI (lambda=%f)"%(lvals[i],lm[i])
        print "-----------------------------------------------------"
        print "STD", intrins_dev[i]
        print "ABS RSME", abs_error[i]
        print "RMSE = %.4f %%"%intrins_error[i]
#
#    print "--------------------------------"
#    print "RESULTS FOR L=0 MODULI (lambda=%f)"%(lval[0],lm[0])
#    print "-----------------------------------------------------"
#    print "STD", intrins_dev[0]
#    print "ABS RSME", abs_error[0]
#    print "RMSE = %.4f %%"%intrins_error[0]
#    print "-----------------------------------------------------"
#    print "RESULTS FOR L=2 MODULI (lambda=%f)"%(lval[1],lm[1])
#    print "-----------------------------------------------------"
#    print "STD",intrins_dev[1]
#    print "ABS RMSE",abs_error[1]
#    print "RMSE = %.4f %%"%intrins_error[1]

###############################################################################################################################

def add_command_line_arguments_learn(parsetext):
    parser = argparse.ArgumentParser(description=parsetext)
    parser.add_argument("-lm", "--lmda", nargs='+', help="Lambda values list for KRR calculation")
    parser.add_argument("-ftr", "--ftrain",type=float, help="Fraction of data points used for testing")
    parser.add_argument("-t", "--tensors", help="File containing tensors")
    parser.add_argument("-k0", "--kernel0", help="File containing L=0 kernel")
    parser.add_argument("-k2", "--kernel2", help="File containing L=2 kernel")
    parser.add_argument("-sel", "--select",nargs='+', help="Select maximum training partition")
    parser.add_argument("-rdm", "--random",type=int, help="Number of random training points")
    args = parser.parse_args()
    return args

###############################################################################################################################

def set_variable_values_learn(args):
    lm0=0.01
    lm1=0.01
    lm2=0.01
    lm3=0.01
    lm = [lm0,lm1,lm2,lm2]
    if args.lmda:
        lmlist = args.lmda
        # This list will either be separated by spaces or by commas (or will not be allowed).
        # We will be a little forgiving and allow a mixture of both.
        if sum([lmlist[i].count(',') for i in xrange(len(lmlist))]) > 0:
            for i in xrange(len(lmlist)):
                lmlist[i] = lmlist[i].split(',')
            lmlist = np.concatenate(lmlist)
        if (len(lmlist)%2 != 0):
            print "Error: list of lambdas must have the format n,lambda[n],m,lambda[m],..."
            sys.exit(0)
        for i in xrange(len(lmlist)/2):
            nval = int(lmlist[2*i])
            lmval = float(lmlist[2*i+1])
            lm[nval] = lmval

    ftrain=1 
    if args.ftrain:
        ftr = args.ftrain 

    if args.tensors:
        tfile = args.tensors
    else:
        print "Tensors file must be specified!"
        sys.exit(0)
    tens=[line.rstrip('\n') for line in open(tfile)]

    print ""
    print "Loading kernel matrices..."

    if args.kernel0:
        kfile0 = args.kernel0
    else:
        print "Kernel file must be specified!"
        sys.exit(0)
    kernel0 = np.loadtxt(kfile0,dtype=float)

    if args.kernel2:
        kfile2 = args.kernel2
    else:
        print "Kernel file must be specified!"
        sys.exit(0)
    # Read in L=2 kernel
    kernel2 = np.loadtxt(kfile2,dtype=float)

    beg = 0
    end = int(len(tens)/2)
    sel = [beg,end]
    if args.select:
        sellist = args.select
        for i in xrange(len(sellist)):
            sel[0] = int(sellist[0])
            sel[1] = int(sellist[1])

    rdm = 0
    if args.random:
        rdm = args.random

    return [lm[0],lm[2],ftr,tens,kernel0,kernel2,sel,rdm]

###############################################################################################################################

if __name__ == '__main__':
    # Read in all arguments and call the main function.
    args = add_command_line_arguments_learn("SA-GPR for rank-2 tensors")
    [lm0,lm2,fractrain,alps,kernel0_flatten,kernel2_flatten,sel,rdm] = set_variable_values_learn(args)
    do_sagpr2([lm0,lm2],fractrain,alps,[kernel0_flatten,kernel2_flatten],sel,rdm)
