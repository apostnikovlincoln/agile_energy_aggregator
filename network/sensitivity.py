# -*- coding: utf-8 -*-
"""
Created on Thu May 02 13:48:06 2019

@author: qsb15202
"""

####### Importing the OpenDSS Engine  #########
import win32com.client
import scipy.io
import pandas as pd
import numpy as np
from basicBuild import runDSS    #buildDSS runs the OpenDSS Load Flow

dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
dssText = dssObj.Text

###### Set voltage Limits ######
v_upper = 1.05
v_lower = 0.95

###### Initialise variables  #####

Loads = pd.read_csv("Loads.txt",delimiter=' ', names=['New','Load','Phases','Bus1','kV','kW','PF','Daily'] )

DSSCircuit = dssObj.ActiveCircuit
DSSLoads=DSSCircuit.Loads;

Agents=0

##### Run Load flow (BuildDSS) for each zone #############
delta = 0
Flags = runDSS(flex,Agents)
    
voltagesBase = pd.read_csv('LVTest_EXP_VOLTAGES.csv', names=["Bus","BasekV","Node1","Mag1","Ang1","pu1","Node2","Mag2","Ang2","pu2","Node3","Mag3","Ang3","pu3"],header=0)
overloadsBase = pd.read_csv('LVTest_EXP_OVERLOADS.csv', names=["Element","Terminal","I1","AmpsOver","kVAOver","%Normal","%Emergency","I2","I2/I1","I0","I0/I1"], header=0) 

dssText.Command="plot Type = Circuit Quantity =Current" 

### Voltage Output#####

allvB = voltagesBase['pu1'].append(voltagesBase['pu2']).append(voltagesBase['pu3'])
allvminB = allvB.min()
allvmaxB = allvB.max()
print("Vmin and Vmax " +str(round(allvminB,3))+ ", "+str(round(allvmaxB,3)))

####Thermal Overloads 

over = overloadsBase['AmpsOver'].max()*0.41
over = np.nan_to_num(over)
print("Max thermal overload by approx " +str(round(over,4))+ " kVA")


if allvmin < v_lower:
    print("Voltage Lower Bound Violation By " +str(round((v_lower-allvmin),2))+ " V")

if allv.max() > v_upper:
    SenseVU = pd.DataFrame(index=(range(0,len(Flags['Agent']))),columns=['Bus.Phase','Sensitivity'], dtype=float)
    SenseVU['Bus.Phase'][0:31] = Loads['Bus1'][1:32].str[6:]
    #Turn up demends / turn down generation
    print("upper voltage violation (above 1.05 p.u)")
    flex = 10
    for i in range(0,len(Flags['Agent'])):
        Flags['Agent'] = 0
        Flags['Agent'][i]=1
        flags = runDSS(flex,Flags['Agent'])  
        
        #### Calculate sensitivity of agent on max voltage
        
        voltages = pd.read_csv('LVTest_EXP_VOLTAGES.csv', names=["Bus","BasekV","Node1","Mag1","Ang1","pu1","Node2","Mag2","Ang2","pu2","Node3","Mag3","Ang3","pu3"],header=0)
        overloads = pd.read_csv('LVTest_EXP_OVERLOADS.csv', names=["Element","Terminal","I1","AmpsOver","kVAOver","%Normal","%Emergency","I2","I2/I1","I0","I0/I1"], header=0) 
        
        ### Voltage Output#####
    
        allv = voltages['pu1'].append(voltages['pu2']).append(voltages['pu3'])
        allvmin = allv.min()
        allvmax = allv.max()
        #print("Vmin and Vmax " +str(round(allvmin,3))+ ", "+str(round(allvmax,3)))
        
        SenseVU['Sensitivity'][i] = round(allvmax/allvmaxB,3)
        
    print(SenseVU)
    
    
    
    
#    ###### Look for violations and Select Required Flexibility ########
#    voltages = pd.read_csv('LVTest_EXP_VOLTAGES.csv', names=["Bus","BasekV","Node1","Mag1","Ang1","pu1","Node2","Mag2","Ang2","pu2","Node3","Mag3","Ang3","pu3"],header=0)
#    overloads = pd.read_csv('LVTest_EXP_OVERLOADS.csv', names=["Element","Terminal","I1","AmpsOver","kVAOver","%Normal","%Emergency","I2","I2/I1","I0","I0/I1"], header=0)  
#
#    for i in range(0,len(overloads)):
#        for j in range(0,len(zones)):
#            if "Line.LINE"+str(zones[j]) in overloads['Element'][i]:
#                ovzone[i]=zones[j]
#    
#    for i in range(0,len(voltages)):   
#        for j in range(0,len(zones)):
#            if voltages['Bus'][i].startswith(str(zones[j])):
#                vzone[i]=zones[j]
#    
#    overloads['Zone'] = ovzone
#    voltages['Zone'] = vzone
#
#    ### Voltage Output#####
#    
#    allv = voltages['pu1'][voltages['Zone']==zones[k]].append(voltages['pu2'][voltages['Zone']==zones[k]]).append(voltages['pu3'][voltages['Zone']==zones[k]])
#    allvmin[k] = allv.min()
#    allvmax[k] = allv.max()
#    print("Vmin and Vmax " +str(round(allvmin[k],3))+ ", "+str(round(allvmax[k],3)))
#    
#    ####Thermal Overloads 
#    if over[k] >0:
#        over[k] = overloads['AmpsOver'][overloads['Zone']==zones[k]].max()*0.41
#        over[np.isnan(over)]=0
#        print("thermal overload by approx " +str(round(over[k],4))+ " kVA")
#        #######In case of excess Demand, Flexibility is divided by number of loads in a zone#####
#        flex[k] = flex[k] + over[k]/ agents[k]
#        flex[np.isnan(flex)]=0
#        print("zone is " +str(k+1))
#
#        print("flex is "+str(round(flex[k],3))+" kVA")
#    
#    ####Voltage Overloads        
#    if allvmin[k] < v_lower:
#        flex[k] = flex[k]*1.5
#        print("Voltage Lower Bound Violation By " +str(round((v_lower-allvmin[k]),2))+ " V")
#        print("zone is " +str(k+1))
#        print("flex is "+str(round(flex[k],3))+" kVA")
#
#    if allv.max() > v_upper:
#        #Turn up demends / turn down generation
#        print("upper voltage violation (above 1.05 p.u)")
#
#        
#dssText.Command="plot Type = Circuit Quantity =Current"
#
#Total_Flex= flex*agents
#
#for k in range(0,len(zones)):
#    print("Total flex in zone "+str(k+1)+" is " +str(round(Total_Flex[k],2))+ " kVA equally spread across " +str(agents[k])+" agents")
