#!/bin/bash
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
	sudo killall python
	sudo killall -9 ryu-manager
	sudo mn -c
	exit
}

trap ctrlc INT

# Traffic patterns.
# "stag_0.2_0.3" means 20% under the same Edge switch,
# 30% between different Edge switches in the same Pod,
# and 50% between different Pods.
# "random" means choosing the iperf server randomly.
# Change it if needed.
traffics="random1 random2"
#traffics="stag_0.2_0.3 stag_0.3_0.3 stag_0.4_0.3 stag_0.5_0.3 stag_0.6_0.2 stag_0.7_0.2 stag_0.8_0.1"
# Output directory.

  for traffic in $traffics
  do
    echo "EXPERIMENT $NUM_TRAFFICS/$TOTAL_TRAFFICS"

		echo "$(date) Genetico ${geracao} ${p} ${c} ${mut} - $traffic" >> logs.txt

    NUM=1
    NUM_TRAFFICS=$(expr $NUM_TRAFFICS + $NUM)

    # Create iperf peers.
    sudo python ./create_peers.py --k $k --traffic $traffic --fnum $flows_num_per_host
    sleep 1

    sed -i "s/generations=.*[^,]/generations=${geracoes}/g" "./${target}/network_monitor.py"
    sed -i "s/population_size=.*[^,]/population_size=${p}/g" "./${target}/network_monitor.py"
    sed -i "s/crossover_probability=.*[^,]/crossover_probability=${c}/g" "./${target}/network_monitor.py"
    sed -i "s/mutation_probability=.*[^,]/mutation_probability=${mut}/g" "./${target}/network_monitor.py"

    echo "GENETICO"
    dir="$out_dir/$traffic/Genetico_${geracao}_${p}_${c}_${mut}"
    sudo mkdir -p $dir
    sudo mn -c
    sudo python ./genetico/fattree.py --k $k --duration $duration --dir $dir --cpu $cpu

  done

done
