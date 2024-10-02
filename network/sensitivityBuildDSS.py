# -*- coding: utf-8 -*-
"""
Created on Thu May 02 13:48:06 2019

@author: qsb15202
"""

path='C:\\Users\\CalumEdmunds\\Desktop\\Python\\CE_Python_OpenDSSBasic'
##path = "C:\\Users\\qsb15202\Desktop\\AGILE\\CE_Python_LV_11kV\\network_1\\LVTestCase"
##path= "C:\\Users\\qsb15202\\Desktop\\AGILE\\fully_observable_lv_feeder"
#
#
######## Importing the OpenDSS Engine  #########
import win32com.client
import scipy.io
import numpy as np
import pandas as pd
from random import uniform
from random import seed
import os
pd.options.mode.chained_assignment = None 

def runDSS(flex,agents):
    
    dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
    dssText = dssObj.Text
    
    ### Import smartmeter and PV Data
    data = scipy.io.loadmat(str(path)+'\smartmeter.mat')   #Smartmeter
    pvprof =  pd.read_csv('PVProfiles/MaplePV4kW.csv')  #PV
    
    ####### Compile the OpenDSS file using the Master.txt directory#########
    
    dssText.Command="Compile "+str(path)+"\\Master.dss"
    
    ########## Solve the Circuit ############
    
    DSSCircuit = dssObj.ActiveCircuit
    DSSLoads=DSSCircuit.Loads;
    
    ######## Assign PV, Agent, EV Tags and Zone per Load Node ############
    
    Flags=pd.DataFrame(0, index=(range(0,DSSLoads.Count)), columns=['PV','Agent','EV','Zone','Feedback'])
    Flags['PV'][::4]=1     # Every 4th house has PV
    Flags['Agent']=agents  
    #Flags['EV'][::2]=1     # Every 2nd house has an EV (and is also an agent)
    Flags['EV'][[17,20]]=1
    
    ################## Calculating Load for each Demand ############################
    iLoad = DSSLoads.First
    i=0
    while iLoad>0:
        #Flags['Zone'][i]= int(DSSLoads.Name[4])-1   #Zone number set by prefix to laod name in loads file
        ### Demand is set for each household. Generation is added as a negative demand. EV or agent flexible demand can also be added.
        #### Key Inputs from Aggregator: Any flexibility which is part of the aggregator algorithm (could be PV or EV)
        #### Smartmeter 'base load' demand can also be passed from aggregator
        DSSLoads.kW = data['advDayCust1Copy'][36,:,2].max() - pvprof['P_GEN_MIN'].min()*Flags['PV'][i] - 50* Flags['EV'][i]
        
        ## In case of overloads add/subtract flexibility for Agent Nodes
        
        DSSLoads.kW = DSSLoads.kW + flex*Flags['Agent'][i]
        
        iLoad = DSSLoads.Next
        i = i+1
        
    #Limit per house before Constraint = 4.15 kW
    # SPEN 5.5kVA ADMD per household.
    
    DSSCtrlQueue=DSSCircuit.CtrlQueue
    dssObj.Start(0)
    dssText.Command="solve mode=snapshot"
    DSSCircuit.Solution.Solve
    
    ##########  Export Data to CSV ###########
    
    dssText.Command="export Voltages"
    dssText.Command="export Overloads"
    dssText.Command="export Loads"
    dssText.Command="export Currents"
    
    #dssText.Command = "export mon LINE21_PQ_vs_Time";
        
    MonFileName = dssText.Result;
        #### Export number of agents in each zone to FindFlexNeed.py  ######
    
    return Flags

    