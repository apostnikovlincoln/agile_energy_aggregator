# -*- coding: utf-8 -*-
"""
Created on Thu May 02 13:48:06 2019

@author: qsb15202
"""

path = "C:\\Users\\qsb15202\Desktop\\Python\\CE_Python_OpenDSSBasic"
##path = "C:\\Users\\qsb15202\Desktop\\AGILE\\CE_Python_LV_11kV\\network_1\\LVTestCase"
##path= "C:\\Users\\qsb15202\\Desktop\\AGILE\\fully_observable_lv_feeder"
#
#
######## Importing the OpenDSS Enging  #########
import win32com.client
import scipy.io
import numpy as np
import pandas as pd


def runDSS(flex,cust):
    dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
    dssText = dssObj.Text
    
    
    data = scipy.io.loadmat("smartmeter.mat")
    pvprof =  pd.read_csv('PVProfiles/MaplePV4kW.csv')
    
    ####### Compile the OpenDSS file using the Master.txt directory#########
    
    dssText.Command="Compile "+str(path)+"\\Master.dss"
    
    ########## Solve the Circuit ############
    
    DSSCircuit = dssObj.ActiveCircuit
    DSSLoads=DSSCircuit.Loads;
    
    ######## Assign PV, Agent, EV Tags and Zone per Load Node ############
    
    Flags=pd.DataFrame(0, index=(range(0,DSSLoads.Count)), columns=['PV','Agent','EV','Zone'])
    Flags['PV'][::4]=1     # Every 4th house has PV
    Flags['Agent'][::2]=1  # Every 2nd house is an agent
    Flags['EV'][::2]=1     # Every 2nd house has an EV (and is also an agent)
    
    iLoad = DSSLoads.First
    i=0
    while iLoad>0:
        Flags['Zone'][i]= int(DSSLoads.Name[4])-1
        DSSLoads.kW = data['advDayCust1Copy'][36,:,2].max() - pvprof['P_GEN_MIN'].min()*Flags['PV'][i] + 7* Flags['EV'][i]
        
        ## In case of overloads add/subtract flexibility for Agent Nodes
        
        DSSLoads.kW = DSSLoads.kW - flex[Flags['Zone'][i]]*Flags['Agent'][i]
        
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
    
    dssText.Command = "export mon LINE11_PQ_vs_Time";
        
    MonFileName = dssText.Result;
    
    #### Export number of agents in each zone to FindFlexNeed.py  ######
    zones=list(set(Flags['Zone']))
    agents=pd.Series(0,index=zones)
    for i in range(0,len(zones)):
        agents[i] = (Flags['Agent'][Flags['Zone']==zones[i]] == 1).sum()
    return agents