import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import win32com.client


class OpenDSSNetwork:
    
    def __init__(self):
        # __init__ is called when the network object is instantiated
        # writing code like n = OpenDSSNetwork() will call this function
        
        # please change accordingly
        self.path = r"c:\Work\Python\mesa\agile_aggregator_abm\agile\network"
        
        self.engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
        self.engine.Start(0)
        self.text = self.engine.Text
        self.text.Command="Clear"
        self.circuit = self.engine.ActiveCircuit
        print("OpenDSS: "+self.engine.Version)
        self.text.Command="Compile "+self.path+"\Master.dss"
        self.loads=self.circuit.Loads
        
        # get the number of buses from latitude and longitude data
        # the file location_data.csv is used instead of XY_position.csv
        # the only difference is that x and y are swapped
        # since longitude is mapped to x coordinate and latitude is mapped to y coordinate
        # so LatLongCoords should use yx format
        self.location_data = pd.read_csv(self.path+"\location_data.csv")    
        bus_num = self.location_data.shape[0]

        # get the number of smart meters from load data
        loads_data = pd.read_csv(self.path+"\Loads.txt", header = None)   
        smart_meter_ids = []
        for txt in loads_data[0]:
            # here regexp are used to identify buses with loads
            # maybe opendss can provide a more convenient method of extracting these data
            m = re.search('Bus1=([0-9]+)\.[0-9]', txt)
            if m:
                smart_meter_ids.append(int(m.group(1)))


        self.bus_data = self.location_data["Node"].values

        self.geo_data = np.zeros((bus_num, 2))
        self.sm_geo_data = np.zeros((len(smart_meter_ids), 2))
        
        for i in range(bus_num):
            x,y = (self.location_data["X"][i],self.location_data["Y"][i])
            self.geo_data[i] = [x,y]
 
        j=0
        for i,b in enumerate(self.bus_data):
            if b in smart_meter_ids:
                self.sm_geo_data[j] = self.geo_data[i]
                j+=1

        
    def solve(self, load_list):
        # this method (or function) takes a load list as an input
        # and overrides legacy load shapes in Loads.txt
        # it is called in the step() method of the AggregatorModel() object
        # which also renews the load list on every time step
        
        load = self.loads.First
        i=0
        while load>0:
            self.loads.kW = load_list[i]
            load = self.loads.Next
            i = i+1
            
        self.text.Command="Set Mode=Snapshot"            
        self.circuit.Solution.Solve()
        
    def get_congestion_flags(self):
        # empty method so far: this is how network logic can be implemented in the future
        pass

    def csv_export(self):
        self.text.Command="Export Voltages"
        self.text.Command="Export Overloads"
        self.text.Command="Export Loads"
        self.text.Command="Export Currents"
        self.text.Command="Export Mon LINE11_PQ_vs_Time"
        #MonFileName = self.text.Result
    
    def plot_power(self):
        self.text.Command="Plot Circuit Power Max=1000 Dots=n Labels=n"     
    
    def plot_current(self):
        self.text.Command="Plot Circuit Current Max=1000 Dots=n Labels=n"

    def plot_voltage(self):
        self.text.Command="Plot Circuit Voltage Max=1000 Dots=n Labels=n"        
        
    def plot_network(self, load_list=[]):
        # this method plots the network as a coloured scatterplot
        
        ax = plt.gca() 
        
        # axes limites and ticks
        ax.set_xlim([50,250])
        ax.set_ylim([150,400])
        ax.set_xticks(np.arange(50, 251, 50))
        ax.set_yticks(np.arange(150, 401, 50))
        
        # create annotations     :
        for i,txt in enumerate(load_list):
            position = (self.sm_geo_data[i,0], self.sm_geo_data[i,1])
            offset = 2
            ax.annotate(str(round(txt,4))+" kW", position, tuple(pos + offset for pos in position))
        
        fig = plt.gcf()
        fig.set_size_inches(7, 7*(400/350))
        plt.scatter(self.geo_data[2:,0],self.geo_data[2:,1],s=5,marker="o",)
        plt.scatter(self.sm_geo_data[:,0],self.sm_geo_data[:,1],s=30,marker="o",c="green")
        plt.scatter(self.geo_data[0:2,0],self.geo_data[0:2,1],s=30,marker="o",c="red")
        plt.grid()
        plt.show()
        
    def clear(self):
        self.engine.ClearAll

# please uncomment if you want to run this file separately from the rest of the model
# and leave commented if you run console_run.py or server_run.py        
# this will create a test load list to check if congestion happens
n = OpenDSSNetwork()
load = n.loads.Count*[8] # load in kW
n.solve(load)
n.plot_network(load)
n.plot_current()
n.clear()
