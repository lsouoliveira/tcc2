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
traffics="stag_0.2_0.3"
#traffics="stag_0.2_0.3 stag_0.3_0.3 stag_0.4_0.3 stag_0.5_0.3 stag_0.6_0.2 stag_0.7_0.2 stag_0.8_0.1"
# Output directory.
out_dir="./genetico_params_results_${k}"
sudo rm -f -r out_dir 
sudo mkdir -p $out_dir

num_elements="0"
geracoes=(10 100 100 50 50 25 25)
populacao=(10 25 10 50 25 50 25)
crossover=(0.6 0.6 0.6 0.6 0.6 0.6 0.6)
mutacao=(0.25 0.25 0.25 0.25 0.25 0.25 0.25)

target="genetico"

for i in $num_elements
do
  geracao=${geracoes[$i]}
  p=${populacao[$i]}
  c=${crossover[$i]}
  mut=${mutacao[$i]}

  echo "----PARAMS----------"
  echo "geracao: $geracao"
  echo "populacao: $p"
  echo "crossover: $c"
  echo "mutacao: $mut"
  echo "--------------------"

  NUM_TRAFFICS=1
  TOTAL_TRAFFICS=4

  # Run experiments.
  for traffic in $traffics
  do
    echo "EXPERIMENT $NUM_TRAFFICS/$TOTAL_TRAFFICS"

    NUM=1
    NUM_TRAFFICS=$(expr $NUM_TRAFFICS + $NUM)

    # Create iperf peers.
    sudo python ./../../exp_EFattree/create_peers.py --k $k --traffic $traffic --fnum $flows_num_per_host
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
