from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx
import csv
from .network import OpenDSSNetwork

from mesa.space import NetworkGrid


class AggregatorModel(Model):

    def __init__(self, num_agents=7, num_nodes=10):
        
        # please change accordingly
        self.path = r"c:\Work\Python\mesa\agile_aggregator_abm\agile"
        
        self.num_agents = num_agents
        self.num_nodes = num_nodes if num_nodes >= self.num_agents else self.num_agents
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=0.5)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={
                    #"Gini": compute_gini,
                    "Household": lambda _: _.schedule.agents[0].household,
                    "PV": lambda _: _.schedule.agents[0].pv,
                    "EV": lambda _: _.schedule.agents[0].ev,
                    "Demand": lambda _: _.schedule.agents[0].demand,
                    "Surplus": lambda _: _.schedule.agents[0].surplus                     
            },
            agent_reporters={
                    "Resource": lambda _: _.resource, 
                    "Household": lambda _: _.household,
                    "PV": lambda _: _.pv,
                    "EV": lambda _: _.ev,
                    "Demand": lambda _: _.demand,
                    "Surplus": lambda _: _.surplus                    
            }
        )

        list_of_random_nodes = self.random.sample(self.G.nodes(), self.num_agents)

        # read a 24 hr baseline household profile (5-minute intervals)
        with open(self.path+"\data\household_profile.csv") as hhp:
            csv_reader = csv.reader(hhp)
            load = [row for idx, row in enumerate(csv_reader) if idx==0]
            household_profile = [float(x) for x in load[0]]
            
        # read a 24 hr reference pv profile (minute-by-minute data)
        with open(self.path+"\data\pv_profile.csv") as pvp:
            csv_reader = csv.reader(pvp)
            load = [row for idx, row in enumerate(csv_reader) if idx==0]
            pv_profile = [float(x) for x in load[0]]
            
        # read a 24 hr reference ev profile (10-minute intervals)
        with open(self.path+"\data\ev_profile.csv") as evp:
            csv_reader = csv.reader(evp)
            load = [row for idx, row in enumerate(csv_reader) if idx==0]
            ev_profile = [float(x) for x in load[0]]  
            
        # shrink pv profile to 288 data points (5-minute intervals)
        pv_profile = pv_profile[0::5]   
            
        # beef ev profile up to 288 data points (5-minute intervals)
        ev_profile = [val for val in ev_profile for _ in (0, 1)]

        # create agents
        for i in range(self.num_agents):
            a = ProsumerAgent(i, self, household_profile, pv_profile, ev_profile)
            self.schedule.add(a)
            # add the agent to a random node
            self.grid.place_agent(a, list_of_random_nodes[i])

        self.running = True
        self.datacollector.collect(self)
        
        # instantiate the OpenDSS network
        self.nt = OpenDSSNetwork()
        
    def loads(self):
        return [self.schedule.agents[i].demand for i in range(self.num_agents)]
        
    def network_state(self):        
        self.nt.plot_network(self.loads())

    def step(self):
        # advance agents
        self.schedule.step()
        
        # demand vector
        load_list = self.loads()
        
        # solve OpenDSS network in a snapshot mode
        self.nt.solve(load_list)
        
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class ProsumerAgent(Agent):

    def __init__(self, unique_id, model, household_profile, pv_profile, ev_profile):
        super().__init__(unique_id, model)

        # store reference profiles
        self.household_profile = household_profile
        self.pv_profile = pv_profile
        self.ev_profile = ev_profile
        
        # initial conditions
        self.resource = 1
        self.ts = 0
        self.household = self.household_profile[self.ts]        
        self.pv = self.pv_profile[self.ts]
        self.ev = self.ev_profile[self.ts]
        self.demand = self.household + self.ev - self.pv
        self.surplus = 0
        if self.demand < 0:
            self.surplus = -self.demand
            self.demand = 0

    def move(self):
        possible_steps = [node for node in self.model.grid.get_neighbors(self.pos, include_center=False) if
                          self.model.grid.is_cell_empty(node)]
        if len(possible_steps) > 0:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def share_resource(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        neighbors = self.model.grid.get_cell_list_contents(neighbors_nodes)
        if len(neighbors) > 0:
            other = self.random.choice(neighbors)
            other.resource += 1
            self.resource -= 1

    def step(self):
        self.move()
        if self.resource > 0:
            self.share_resource()
        self.ts += 1
        self.household = self.household_profile[self.ts]        
        self.pv = self.pv_profile[self.ts]
        self.ev = self.ev_profile[self.ts]
        self.demand = self.household + self.ev - self.pv
        self.surplus = 0
        if self.demand < 0:
            self.surplus = -self.demand
            self.demand = 0


class AggregatorAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.resource = 1

    def aggregate_loads(self):
        pass

    def step(self):
        pass