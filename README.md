# TCC 2

## Requirements
- Python 2.7

### Installing dependencies

1. Install pip for python 2.7

```bash
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
```

2. Install the required python packages

```bash
sudo pip2 install mininet networkx numpy matplotlib ryu==4.3
```
3. Install the following package

```bash
sudo apt install bwm-ng
```

## Getting Started

Before running the experiments do the following steps:

### 1. Update `config.py`

- tests/Hedera/config.py
- tests/guloso/config.py
- tests/genetico/config.py

Where:

- k: number of pods in the target Fat-Tree
- fanout: the same as `k`
- k_paths: number of possible paths to consider in `guloso` strategy (network_awereness.py#all_k_shortest_paths)

> Do not change `weight`

### 2. Update `setting.py`

- tests/Hedera/setting.py
- tests/guloso/setting.py
- tests/genetico/setting.py

Change `MAX_CAPACITY` to match the max capacity of link in the target Fat-tree

> For 100 Mbits links, set MAX_CAPACITY to 100000

### 3. Update `fattree.py`

- tests/Hedera/fattree.py
- tests/guloso/fattree.py
- tests/genetico/fattree.py

In the method `run_experiment` change the following method parameters:

- bw_c2a
- bw_a2e
- bw_e2h

These parameters represent the capacity of link of the target Fat-tree.

> To create links with 100 Mbits of capacity, set the parameters as 100
4
### 4. Update `run_project.sh`

This script will run ECMP, Hedera and Guloso for the traffic patterns of choice. The results will be placed at ./results/result_k where k is the number of pods in the Fat-Tree used.

Change `traffics` to choose which traffic patterns to generate in experiments. There's a brief description of each available pattern. It's possible to run the same pattern multiple times, just add a number after `stag` or `random`.

### 5. Update `run_genetic_for_diff_params.sh`

This script will run the genetic algorithm for different sets of parameters. The results will be placed at ./results/genetico_results_k where k is the number of pods in the target Fat-Tree. It's important to use the same traffic patterns and peers as the ones used with ECMP, Hedera and guloso.

Change the following variables as needed. They represent the parameters that will be passed to the genetic algorithm during experiments.

- num_elements: list of ordered numbers that represent the index of every set of parameters.
- geracoes: list of possible iterations.
- populacao: list of possible population sizes.
- crossover: list of probabilities of crossover.
- mutacao: list of probabilities of mutation.

### 5. Generate the peers

Update the file `./iperf_peers_traffics`. Change the variable `traffics` and choose which traffic patterns to use, it must be the same as the ones from `run_project.sh` and `run_genetic_for_diff_params.sh`. Then run the following command:

```bash
./generate_peers k
```

Where `k` is the number of pods in the target Fat-Tree.

> It's possible to change the variable `flows_num_per_host` in the script to match the same parameter passed to `run_project.sh` and `run_genetic_for_diff_params.sh`

### 6. Run the experiments

To run the experiments for ECMP, Hedera, and guloso, use the following command:

```bash
sudo ./run_project K NUM_THREADS NUM_FLOWS DURATION
```

To run the experiments for the genetic algorithm, use the following command:

```bash
sudo ./run_genetic_for_diff_params.sh k num_threads num_flows duration
```

where:

- k: number of pods in the target Fat-Tree
- num_threads: how many threads to use in the experiments
- num_flows: how many flows per host will be generated each time
- duration: how long the traffic patterns will be generated

> It's important to update `config.py` and `setting.py` always that `k` changes.


