#/bin/bash
# Copyright (C) 2016 Huang MaChi at Chongqing University
# of Posts and Telecommunications, China.

k=$1
cpu=$2
flows_num_per_host=$3   # number of iperf flows per host.
duration=$4

# Exit on any failure.
set -e

# Check for uninitialized variables.
set -o nounset

ctrlc() {
  killall python
  killall -9 ryu-manager
  mn -c
  exit
}

trap ctrlc INT

# Traffic patterns.
# "stag_0.2_0.3" means 20% under the same Edge switch,
# 30% between different Edge switches in the same Pod,
# and 50% between different Pods.
# "random" means choosing the iperf server randomly.
# Change it if needed.
traffics="stag1_0.2_0.3 stag2_0.2_0.3 stag1_0.4_0.3 stag2_0.4_0.3 stag1_0.5_0.3 stag2_0.5_0.3 random1 random2"
#traffics="stag1_0.2_0.3"
#traffics="stag_0.2_0.3 stag_0.3_0.3 stag_0.4_0.3 stag_0.5_0.3 stag_0.6_0.2 stag_0.7_0.2 stag_0.8_0.1"
# Output directory.
out_dir="./results/result_${k}"
rm -f -r $out_dir 
mkdir -p $out_dir

NUM_TRAFFICS=0
TOTAL_TRAFFICS=8

# Run experiments.
for traffic in $traffics
do
  echo "EXPERIMENT $NUM_TRAFFICS/$TOTAL_TRAFFICS"

NUM=1
NUM_TRAFFICS=$(expr $NUM_TRAFFICS + $NUM)


echo "$(date) $traffic $NUM_TRAFFICS / $TOTAL_TRAFFICS" >> logs.txt

# Create iperf peers.
sudo rm -f ./iperf_peers.pyc
sudo cp -rf "./iperf_peers_traffics/iperf_peers_${traffic}_${k}.py" ./iperf_peers.py
sleep 1

# ECMP
echo "ECMP"
dir=$out_dir/$traffic/ECMP
mkdir -p $dir
mn -c
sudo python ./ecmp/fattree.py --k $k --duration $duration --dir $dir --cpu $cpu

# Hedera
echo "Hedera"
dir=$out_dir/$traffic/Hedera
mkdir -p $dir
mn -c
sudo python ./Hedera/fattree.py --k $k --duration $duration --dir $dir --cpu $cpu

# Guloso
echo "GULOSO"
dir=$out_dir/$traffic/Guloso
mkdir -p $dir
mn -c
sudo python ./guloso/fattree.py --k $k --duration $duration --dir $dir --cpu $cpu

done
