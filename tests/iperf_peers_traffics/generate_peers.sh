#!/bin/bash

k=$1
flows_num_per_host=1
traffics="stag1_0.2_0.3 stag2_0.2_0.3 stag1_0.4_0.3 stag2_0.4_0.3 stag1_0.5_0.3 stag2_0.5_0.3 random1 random2"

for traffic in $traffics
do
  echo $traffic
  sudo python ./create_peers.py --k $k --traffic $traffic --fnum $flows_num_per_host
  sleep 1

  mv iperf_peers.py "iperf_peers_${traffic}_$k.py"
done
