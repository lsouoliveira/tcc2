class Flow:
    def __init__(self, src=None, dst=None, demand=None, match=None):
        self.src = src
        self.dst = dst
        self.demand = demand
        self.match = match

    def __str__(self):
        return str({
            'src': self.src,
            'dst': self.dst,
            'demand': self.demand,
            'priority': self.priority,
            'match': self.match,
            'size': self.size,
            'match': self.match,
            'timestamp': self.timestamp
        })

    def __repr__(self):
        return str(self)


def from_dict(flow_data):
    flow = Flow()

    flow.src = flow_data['src']
    flow.dst = flow_data['dst']
    flow.priority = flow_data['priority']
    flow.match = flow_data['match']
    flow.demand = flow_data['demand']
    flow.size = flow_data['size']
    flow.match = flow_data['match']
    flow.timestamp = flow_data['timestamp']

    return flow
