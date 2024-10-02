from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from .model import AggregatorModel


def network_portrayal(G):
    # creates a dictionary that is passed to JSON for visualisation
    # in this case it is a simple random graph with agents assigned to its nodes
    
    portrayal = dict()
    portrayal['nodes'] = [{'id': node_id,
                           'size': 3 if agents else 1,
                           'color': '#CC0000' if not agents or agents[0].resource == 0 else '#007959',
                           'label': None if not agents else 'Agent:{} Resource:{}kW'.format(agents[0].unique_id,
                                                                                        round(agents[0].surplus,4))
                           }
                          for (node_id, agents) in G.nodes.data('agent')]

    portrayal['edges'] = [{'id': edge_id,
                           'source': source,
                           'target': target,
                           'color': '#000000'
                           }
                          for edge_id, (source, target) in enumerate(G.edges)]

    return portrayal


grid = NetworkModule(network_portrayal, 500, 500, library='sigma')

household_chart = ChartModule([
    {"Label": "Household", "Color": "Grey"}],
    data_collector_name='datacollector'
)
pv_chart = ChartModule([
    {"Label": "PV", "Color": "Grey"}],
    data_collector_name='datacollector'
)
ev_chart = ChartModule([
    {"Label": "EV", "Color": "Grey"}],
    data_collector_name='datacollector'
)
demand_chart = ChartModule([
    {"Label": "Demand", "Color": "Grey"}],
    data_collector_name='datacollector'
)
surplus_chart = ChartModule([
    {"Label": "Surplus", "Color": "Grey"}],
    data_collector_name='datacollector'
)

# gini coefficient used for testing of resource sharing
# =============================================================================
# gini_chart = ChartModule([
#     {"Label": "Gini", "Color": "Grey"}],
#     data_collector_name='datacollector'
# )
# =============================================================================

figs = [grid, household_chart, pv_chart, ev_chart, demand_chart, surplus_chart]

model_params = {
    "num_agents": UserSettableParameter('slider', "Number of agents", 7, 2, 100, 1,
                                        description="Choose how many agents to include in the model"),
    "num_nodes": UserSettableParameter('slider', "Number of nodes", 10, 3, 120, 1,
                                       description="Choose how many nodes to include in the model, with at "
                                                   "least the same number of agents")
}

# localhost server used for visualisation of both the model (graph) and figures (power profiles)
server = ModularServer(AggregatorModel, figs, "Aggregator Model", model_params)