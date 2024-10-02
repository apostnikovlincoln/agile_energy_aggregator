# -*- coding: utf-8 -*-
"""
Created on Fri May 03 14:29:48 2019

@author: qsb15202
"""

import scipy.io
import numpy as np

data = scipy.io.loadmat("smartmeter.mat")

#for i in data:
#	if '__' not in i and 'readme' not in i:
#		np.savetxt(("smartmeter/"+i+".csv"),data[i],delimiter=',')

