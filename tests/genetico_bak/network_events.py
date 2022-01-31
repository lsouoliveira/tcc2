from ryu.controller import event
from network_models import Flow

class FlowsDetected(event.EventBase):
    def __init__(self, flows):
        super(FlowsDetected, self).__init__()

        self.flows = flows