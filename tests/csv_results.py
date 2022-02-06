# -*- coding: utf-8 -*-
# Copyright (C) 2016 Huang MaChi at Chongqing University
# of Posts and Telecommunications, Chongqing, China.
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

import argparse
import re
import numpy as np
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description="Plot EFattree experiments' results")
parser.add_argument('--k', dest='k', type=int, default=4, choices=[4, 8], help="Switch fanout number")
parser.add_argument('--duration', dest='duration', type=int, default=60, help="Duration (sec) for each iperf traffic generation")
parser.add_argument('--dir', dest='out_dir', help="Directory to store outputs")
args = parser.parse_args()

apps = []

SINGLE_TRAFFIC_COUNT = 2

def read_file_1(file_name, delim=','):
    """
        Read the bwmng.txt file.
    """
    read_file = open(file_name, 'r')
    lines = read_file.xreadlines()
    lines_list = []
    for line in lines:
        line_list = line.strip().split(delim)
        lines_list.append(line_list)
    read_file.close()

    # Remove the last second's statistics, because they are mostly not intact.
    last_second = lines_list[-1][0]
    _lines_list = lines_list[:]
    for line in _lines_list:
        if line[0] == last_second:
            lines_list.remove(line)

    return lines_list

def read_file_2(file_name):
    """
        Read the first_packets.txt and successive_packets.txt file.
    """
    read_file = open(file_name, 'r')
    lines = read_file.xreadlines()
    lines_list = []
    for line in lines:
        if line.startswith('rtt') or line.endswith('ms\n'):
            lines_list.append(line)
    read_file.close()
    return lines_list

def calculate_average(value_list):
    average_value = sum(map(float, value_list)) / len(value_list)
    return average_value

def get_throughput(throughput, traffic, app, input_file):
    """
        csv output format:
            (Type rate)
        unix_timestamp;iface_name;bytes_out/s;bytes_in/s;bytes_total/s;bytes_in;bytes_out;packets_out/s;packets_in/s;packets_total/s;packets_in;packets_out;errors_out/s;errors_in/s;errors_in;errors_out\n
        (Type svg, sum, max)
        unix timestamp;iface_name;bytes_out;bytes_in;bytes_total;packets_out;packets_in;packets_total;errors_out;errors_in\n
        The bwm-ng mode used is 'rate'.

        throughput = {
                'stag1_0.5_0.3':
                {
                    'realtime_bisection_bw': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'realtime_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'accumulated_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'normalized_total_throughput': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                'stag2_0.5_0.3':
                {
                    'realtime_bisection_bw': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'realtime_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'accumulated_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'normalized_total_throughput': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                ...
                }
    """
    global apps

    full_bisection_bw = 100.0 * (args.k ** 3 / 4)   # (unit: Mbit/s)
    lines_list = read_file_1(input_file)
    first_second = int(lines_list[0][0])
    column_bytes_out_rate = 2   # bytes_out/s
    column_bytes_out = 6   # bytes_out

    if app == 'NonBlocking':
        switch = '1001'
    elif app in apps:
        switch = '3[0-9][0-9][0-9]'
    else:
        pass
    sw = re.compile(switch)

    if not throughput.has_key(traffic):
        throughput[traffic] = {}

    if not throughput[traffic].has_key('realtime_bisection_bw'):
        throughput[traffic]['realtime_bisection_bw'] = {}
    if not throughput[traffic].has_key('realtime_throughput'):
        throughput[traffic]['realtime_throughput'] = {}
    if not throughput[traffic].has_key('accumulated_throughput'):
        throughput[traffic]['accumulated_throughput'] = {}
    if not throughput[traffic].has_key('normalized_total_throughput'):
        throughput[traffic]['normalized_total_throughput'] = {}

    if not throughput[traffic]['realtime_bisection_bw'].has_key(app):
        throughput[traffic]['realtime_bisection_bw'][app] = {}
    if not throughput[traffic]['realtime_throughput'].has_key(app):
        throughput[traffic]['realtime_throughput'][app] = {}
    if not throughput[traffic]['accumulated_throughput'].has_key(app):
        throughput[traffic]['accumulated_throughput'][app] = {}
    if not throughput[traffic]['normalized_total_throughput'].has_key(app):
        throughput[traffic]['normalized_total_throughput'][app] = 0

    for i in xrange(args.duration + 1):
        if not throughput[traffic]['realtime_bisection_bw'][app].has_key(i):
            throughput[traffic]['realtime_bisection_bw'][app][i] = 0
        if not throughput[traffic]['realtime_throughput'][app].has_key(i):
            throughput[traffic]['realtime_throughput'][app][i] = 0
        if not throughput[traffic]['accumulated_throughput'][app].has_key(i):
            throughput[traffic]['accumulated_throughput'][app][i] = 0

    for row in lines_list:
        iface_name = row[1]
        if iface_name not in ['total', 'lo', 'eth0', 'enp0s3', 'enp0s8', 'docker0']:
            if switch == '3[0-9][0-9][0-9]':
                if sw.match(iface_name):
                    if int(iface_name[-1]) > args.k / 2:   # Choose down-going interfaces only.
                        if (int(row[0]) - first_second) <= args.duration:   # Take the good values only.
                            throughput[traffic]['realtime_bisection_bw'][app][int(row[0]) - first_second] += float(row[column_bytes_out_rate]) * 8.0 / (10 ** 6)   # Mbit/s
                            throughput[traffic]['realtime_throughput'][app][int(row[0]) - first_second] += float(row[column_bytes_out]) * 8.0 / (10 ** 6)   # Mbit
            elif switch == '1001':   # Choose all the interfaces. (For NonBlocking Topo only)
                if sw.match(iface_name):
                    if (int(row[0]) - first_second) <= args.duration:
                        throughput[traffic]['realtime_bisection_bw'][app][int(row[0]) - first_second] += float(row[column_bytes_out_rate]) * 8.0 / (10 ** 6)   # Mbit/s
                        throughput[traffic]['realtime_throughput'][app][int(row[0]) - first_second] += float(row[column_bytes_out]) * 8.0 / (10 ** 6)   # Mbit
            else:
                pass

    for i in xrange(args.duration + 1):
        for j in xrange(i+1):
            throughput[traffic]['accumulated_throughput'][app][i] += throughput[traffic]['realtime_throughput'][app][j]   # Mbit

    throughput[traffic]['normalized_total_throughput'][app] = throughput[traffic]['accumulated_throughput'][app][args.duration] / (full_bisection_bw * args.duration)   # percentage

    return throughput

def get_value_list_1(value_dict, traffic, item, app):
    """
        Get the values from the "throughput" data structure.
    """
    value_list = []
    for i in xrange(args.duration + 1):
        value_list.append(value_dict[traffic][item][app][i])
    return value_list

def get_average_bisection_bw(value_dict, traffics, app):
    value_list = []
    complete_list = []
    accumulated_throughput = []
    for traffic in traffics:
        complete_list.append(value_dict[traffic]['accumulated_throughput'][app][args.duration] / float(args.duration))
        accumulated_throughput.append(value_dict[traffic]['accumulated_throughput'][app][args.duration])
    # print "accumulated_throughput:", accumulated_throughput
    for i in xrange(5):
        value_list.append(calculate_average(complete_list[(i * SINGLE_TRAFFIC_COUNT): (i * SINGLE_TRAFFIC_COUNT + SINGLE_TRAFFIC_COUNT)]))
    return value_list

def get_value_list_2(value_dict, traffics, item, app):
    """
        Get the values from the "throughput", "first_packet_delay" and "average_delay" data structure.
    """
    value_list = []
    complete_list = []
    for traffic in traffics:
        complete_list.append(value_dict[traffic][item][app])
    for i in xrange(5):
        value_list.append(calculate_average(complete_list[(i * SINGLE_TRAFFIC_COUNT): (i * SINGLE_TRAFFIC_COUNT + SINGLE_TRAFFIC_COUNT)]))
    return value_list

def get_value_list_3(value_dict, traffics, items, app):
    """
        Get the values from the "first_packet_delay" and "average_delay" data structure.
    """
    value_list = []
    send_list = []
    receive_list = []
    for traffic in traffics:
        send_list.append(value_dict[traffic][items[0]][app])
        receive_list.append(value_dict[traffic][items[1]][app])
    for i in xrange(5):
        value_list.append((sum(send_list[(i * SINGLE_TRAFFIC_COUNT): (i * SINGLE_TRAFFIC_COUNT + SINGLE_TRAFFIC_COUNT)]) - sum(receive_list[(i * SINGLE_TRAFFIC_COUNT): (i * SINGLE_TRAFFIC_COUNT + SINGLE_TRAFFIC_COUNT)])) / float(sum(send_list[(i * SINGLE_TRAFFIC_COUNT): (i * SINGLE_TRAFFIC_COUNT + SINGLE_TRAFFIC_COUNT)])))

    return value_list

def get_delay(delay, traffic, keys, app, input_file):
    """
        first_packet_delay = {
                'stag1_0.5_0.3':
                {
                    'average_first_packet_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
                    'first_packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                'stag2_0.5_0.3':
                {
                    'average_first_packet_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
                    'first_packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                ...
                }

        average_delay = {
                'stag1_0.5_0.3':
                {
                    'average_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
                    'packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...},
                    'mean_deviation_of_round_trip_delay': {'EFattree':x%, 'ECMP':x%, ...},
                    },
                'stag2_0.5_0.3':
                {
                    'average_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
                    'packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...},
                    'mean_deviation_of_round_trip_delay': {'EFattree':x%, 'ECMP':x%, ...},
                    },
                ...
                }
    """
    if not delay.has_key(traffic):
        delay[traffic] = {}

    for i in range(len(keys)):
        if not delay[traffic].has_key(keys[i]):
            delay[traffic][keys[i]] = {}

    for i in range(len(keys)):
        if not delay[traffic][keys[i]].has_key(app):
            delay[traffic][keys[i]][app] = 0

    lines_list = read_file_2(input_file)
    average_delay_list = []
    if len(keys) == 3:
        for line in lines_list:
            if line.startswith('rtt'):
                average_delay_list.append(float(line.split('/')[4]))
            else:
                delay[traffic]['first_packet_total_send'][app] += int(line.split(' ')[0])
                delay[traffic]['first_packet_total_receive'][app] += int(line.split(' ')[3])
        # print "traffic:", traffic
        # print "app:", app
        delay[traffic][keys[0]][app] = calculate_average(average_delay_list)
    elif len(keys) == 4:
        mean_deviation_list = []
        for line in lines_list:
            if line.startswith('rtt'):
                average_delay_list.append(float(line.split('/')[4]))
                mean_deviation_list.append(float((line.split('/')[6]).split(' ')[0]))
            else:
                delay[traffic]['total_send'][app] += int(line.split(' ')[0])
                delay[traffic]['total_receive'][app] += int(line.split(' ')[3])
        delay[traffic][keys[0]][app] = calculate_average(average_delay_list)
        delay[traffic][keys[1]][app] = calculate_average(mean_deviation_list)

    return delay

def plot_results():
    """
        Plot the results:
            1. Plot average bisection bandwidth
        2. Plot normalized total throughput
        3. Plot average first-packet round-trip delay of delay-sensitive traffic
        4. Plot first-packet loss rate of delay-sensitive traffic
        5. Plot average packet round-trip delay of delay-sensitive traffic
        6. Plot packet loss rate of delay-sensitive-traffic
        7. Plot mean deviation of round-trip delay of delay-sensitive traffic

        throughput = {
                'stag1_0.5_0.3':
                {
                    'realtime_bisection_bw': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'realtime_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'accumulated_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'normalized_total_throughput': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                'stag2_0.5_0.3':
                {
                    'realtime_bisection_bw': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'realtime_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'accumulated_throughput': {'EFattree':{0:x, 1:x, ..}, 'ECMP':{0:x, 1:x, ..}, ...},
                    'normalized_total_throughput': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                ...
                }

        first_packet_delay = {
                'stag1_0.5_0.3':
                {
                    'average_first_packet_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
                    'first_packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                'stag1_0.5_0.3':
                {
                    'average_first_packet_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
                    'first_packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...}
                    },
                ...
                }
average_delay = {
        'stag1_0.5_0.3':
        {
            'average_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
            'packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...},
            'mean_deviation_of_round_trip_delay': {'EFattree':x%, 'ECMP':x%, ...},
            },
        'stag1_0.5_0.3':
        {
            'average_round_trip_delay': {'EFattree':x, 'ECMP':x, ...},
            'packet_loss_rate': {'EFattree':x%, 'ECMP':x%, ...},
            'mean_deviation_of_round_trip_delay': {'EFattree':x%, 'ECMP':x%, ...},
            },
        ...
        }
"""
    global apps
    full_bisection_bw = 100.0 * (args.k ** 3 / 4)   # (unit: Mbit/s)
    utmost_throughput = full_bisection_bw * args.duration
    # _traffics = "stag1_0.5_0.3 stag2_0.5_0.3 stag1_0.6_0.2 stag2_0.6_0.2 stag1_0.7_0.2 stag2_0.7_0.2 stag1_0.8_0.1 stag2_0.8_0.1"
    _traffics = "stag1_0.2_0.3 stag2_0.2_0.3 stag1_0.4_0.3 stag2_0.4_0.3 stag1_0.5_0.3 stag2_0.5_0.3 random1 random1 random2 random2"
    traffics = _traffics.split(' ')
    traffics_brief = ['stag_0.2_0.3', 'stag_0.4_0.3', 'stag_0.5_0.3', 'random1', 'random2']
    throughput = {}
    first_packet_delay = {}
    average_delay = {}

    geracoes=[100, 100, 100, 50, 50, 25, 25, 100, 50, 25]
    populacao=[100, 25, 10, 50, 25, 50, 25, 50, 10, 25]
    crossover=[0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.8, 0.8, 0.8]
    mutacao=[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.2, 0.1, 0.1]

    apps = ['Genetico_%d_%d_%g_%g' % (geracoes[i], populacao[i], crossover[i], mutacao[i]) for i in range(len(geracoes))] 

    for traffic in traffics:
        for app in apps:
            bwmng_file = args.out_dir + '/%s/%s/bwmng.txt' % (traffic, app)
            throughput = get_throughput(throughput, traffic, app, bwmng_file)
            keys1 = ['average_first_packet_round_trip_delay', 'first_packet_total_send', 'first_packet_total_receive']
            keys2 = ['average_round_trip_delay', 'mean_deviation_of_round_trip_delay', 'total_send', 'total_receive']
            first_packet_file = args.out_dir + '/%s/%s/first_packets.txt' % (traffic, app)
            first_packet_delay = get_delay(first_packet_delay, traffic, keys1, app, first_packet_file)
            successive_packets_file = args.out_dir + '/%s/%s/successive_packets.txt' % (traffic, app)
            average_delay = get_delay(average_delay, traffic, keys2, app, successive_packets_file)

    for traffic_index in range(len(traffics_brief)):
        traffic = traffics_brief[traffic_index]
        csv_output = ""

        csv_output += 'Gerações,Pop.,Crossover,Mutação,Transf.,Transf. Normalizada,Perda de Pacotes,Lat. Bidirecional\n'

        for i in range(len(apps)):
            app = apps[i]

            taxa_de_transferencia = get_average_bisection_bw(throughput, traffics, app)

            item = 'normalized_total_throughput'
            taxa_de_transferencia_normalizada = get_value_list_2(throughput, traffics, item, app)

            items = ['total_send', 'total_receive']
            taxa_de_perda_de_pacotes = get_value_list_3(average_delay, traffics, items, app)

            item = 'average_round_trip_delay'
            latencia = get_value_list_2(average_delay, traffics, item, app)

            print('latencia', latencia)
            print latencia[traffic_index], traffic_index

            csv_output += '%d,%d,%g,%g,%.2k,%.3f,%.5f,%.2f' % (
                    geracoes[i],
                    populacao[i],
                    crossover[i],
                    mutacao[i],
                    taxa_de_transferencia[traffic_index],
                    taxa_de_transferencia_normalizada[traffic_index],
                    taxa_de_perda_de_pacotes[traffic_index],
                    latencia[traffic_index]
            ) + '\n'

        with open('%s/%s.csv' % (args.out_dir, traffic), 'w') as f:
            f.write(csv_output)


if __name__ == '__main__':
    plot_results()
