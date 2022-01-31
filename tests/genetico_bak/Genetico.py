# Copyright (C) 2016 Huang MaChi at Chongqing University
# of Posts and Telecommunications, Chongqing, China.
# Copyright (C) 2016 Li Cheng at Beijing University of Posts
# and Telecommunications. www.muzixing.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -*- coding: utf-8 -*-

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

import network_awareness
import network_monitor
import network_events
import setting
import config
import networkx as nx
from genetic import NetworkGa
import time

CONF = config.CONF

class NetworkController(app_manager.RyuApp):
    '''
    Route flows that are detected by the NetworkMonitor

    Args:
            *args: The variable arguments are passed to RyuApp base class
            kwargs: Apps used by this Ryu app

    Attributes:
            name (str): This Ryu app name
            awareness (Object): Ryu app that calculate demands
            monitor (Object): Ryu app that detect flows
    '''

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {
        'network_awareness': network_awareness.NetworkAwareness,
        'network_monitor': network_monitor.NetworkMonitor}

    _EVENTS = [network_events.FlowsDetected]

    def __init__(self, *args, **kwargs):
        super(NetworkController, self).__init__(*args, **kwargs)

        self.name = 'network_controller'
        self.awareness = kwargs['network_awareness']
        self.monitor = kwargs['network_monitor']
