import networkx as nx
import matplotlib.pyplot as plt
import time

def create_fattree(k=4):
    """Create a fat tree and it visual representation
    """
    num_cores = (k / 2) ** 2
    num_ports = (k / 2)

    # FatTree graph
    fattree = nx.Graph()
    pos = {}

    # Connect cores and aggs switches
    for i in range(num_ports):
        for j in range(num_ports * i, (num_ports * i) + num_ports):
            for l in range(k):
                fattree.add_edge("c{}".format(j), "a{},{}".format(l, i), weight=0)
                # print("c{}".format(j), "a{},{}".format(l, i))

                # # Connect aggs and edges switches
                for m in range(num_ports):
                    fattree.add_edge("a{},{}".format(l, i), "e{},{}".format(l, m), weight=0)
                    # print("a{},{}".format(l, i), "e{},{}".format(l, m))

                    for n in range(num_ports * m, (num_ports * m) + num_ports):
                        fattree.add_edge("e{},{}".format(l, m), "h{},{}".format(l, n), weight=0)

    # Create pos
    # Core
    for i in range(num_cores):
        pos["c{}".format(i)] = (i * 25 + (200 * (k - 1) / 2) - ((num_cores - 1) * 25) / 2, 0)
    
    # Aggregation
    for i in range(k):
        for j in range(num_ports):
            pos["a{},{}".format(i, j)] = (i * 200 + j * 25, -25)

    # Edge
    for i in range(k):
        for j in range(num_ports):
            pos["e{},{}".format(i, j)] = (i * 200 + j * 25, -50)

    # Edge
    for i in range(k):
        for j in range(num_ports):
            pos["e{},{}".format(i, j)] = (i * 200 + j * 25, -50)
    
    # Host
    for i in range(k):
        for j in range(k):
            pos["h{},{}".format(i, j)] = (i * 200 + j * 25 - ((k - 1) * 25 / 2), -75)

    return (fattree, pos)

def get_path_by_switch(G, src, dst, switch):
    for path in nx.all_shortest_paths(G, src, dst):
        if switch in path:
            return path

class Benchmark:
    def __init__(self, namespace=None):
        self.namespace = namespace

    def start(self):
        self.startTime = time.time()
        return self

    def end(self):
        self.endTime = time.time()
        return self

    def total(self):
        return self.endTime - self.startTime

    def print_results(self):
        print(('BENCHMARK: %s: ' % (self.namespace if not self.namespace is None else '')) + str(self.total()))

