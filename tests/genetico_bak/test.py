from utils import create_fattree
import networkx as nx
from genetic import NetworkGa
import matplotlib.pyplot as plt

# Create FatTree
fattree, pos = create_fattree()

# Show FatTree
nx.draw_networkx(fattree, pos=pos)

# plt.show()

# Test the algorithm
demands = [{'src': 'h0,0', 'dst': 'h1,3', 'size': 1, 'interpod': True, 'pod': 0}, {'src': 'h0,0', 'dst': 'h0,2', 'size': 1, 'interpod': False, 'pod': 0}]

# Switches map
core_switches = ["c0", "c1", "c2", "c3"]
agg_switches = [["a0,0", "a0,1"], ["a1,0", "a1,1"], ["a2,0", "a2,1"], ["a3,0", "a3,1"]]

# Create and run the model
ga = NetworkGa(demands,
    core_switches,
    agg_switches,
    fattree,
    100,
    2,
    maximise_fitness=False
)

ga.run()

print(ga.best_individual())
