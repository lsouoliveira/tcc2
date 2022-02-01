# -*- coding: utf-8 -*-
import random
from pyeasyga.pyeasyga import GeneticAlgorithm
import numpy as np
from utils import get_path_by_switch, Benchmark
import time

class NetworkGa(GeneticAlgorithm):
    def __init__(self,
            demands,
            core_switches,
            agg_switches,
            fattree,
            max_capacity,
            generations=100,
            population_size=50,
            crossover_probability=0.8,
            mutation_probability=0.5,
            elitism=True,
            maximise_fitness=True,
            edge_switch_map=None):
        super(NetworkGa, self).__init__([],
                population_size=population_size,
                generations=generations,
                crossover_probability=crossover_probability if len(demands) >= 2 else 0,
                mutation_probability=mutation_probability,
                elitism=elitism,
                maximise_fitness=maximise_fitness)

        self.demands = demands
        self.agg_switches = agg_switches
        self.core_switches = core_switches
        self.fattree = fattree
        self.max_capacity = max_capacity
        self.edge_switch_map = edge_switch_map

        self.fitness_function = self.fitness 
        self.create_individual = self.create_individual_function
        self.selection_function = self.selection
        self.mutate_function = self.mutate

        self.bm = Benchmark('TOTAL_TIME').start()

    def create_individual_function(self, data):
        """Create a individual by demand type
        """
        individual = []

        for demand in self.demands:
            if demand['interpod']:
                individual.append(random.choice(self.core_switches))
            else:
                individual.append(random.choice(self.agg_switches[demand['pod']]))

        return individual

    def mutate(self, individual):
        """Change a random position of a individual based on demand type
        """
        index = random.randint(0, len(individual) - 1)

        if self.demands[index]['interpod']:
            individual[index] = random.choice(self.core_switches)
        else:
            individual[index] = random.choice(self.agg_switches[self.demands[index]['pod']])

    def selection(self, population):        
        # Calculate the sum of all individuals fitness
        fitness_sum = sum(map(lambda x: max(x.fitness, 0.001), population))

        # Calculate a probability for each individual in population
        p_fitness_list = map(lambda x: 1.0 - (float(x.fitness) / fitness_sum), population)
        p_fitness_sum = sum(p_fitness_list)
        p_fitness_normalized = map(lambda x: x / p_fitness_sum, p_fitness_list)

        # Select individual by probability p
        choice = np.random.choice(population, len(population), p=p_fitness_normalized)

        return choice[0]

    def fitness(self, individual, data):
        max_link_utilization = 0

        links_map = {}

        for demand_index in range(len(self.demands)):
            demand = self.demands[demand_index]
            switch = individual[demand_index]

            # path = get_path_by_switch(self.fattree, demand['src'], demand['dst'], switch)
            path = self.edge_switch_map[demand['src']][demand['dst']][switch] 

            for l in range(1, len(path)):
                link = self.fattree[path[l]][path[l - 1]]

                # Current link src and dst for map
                a = b = None

                # Get links current bandwidth
                if links_map.has_key(path[l]) and links_map[path[l]].has_key(path[l - 1]):
                    a = path[l]
                    b = path[l - 1]
                elif links_map.has_key(path[l - 1]) and links_map[path[l - 1]].has_key(path[l]):
                    a = path[l - 1]
                    b = path[l]
                else:
                    if links_map.has_key(path[l]):
                        a = path[l]
                        links_map[a][path[l - 1]] = self.max_capacity - link['bandwidth']
                        b = path[l - 1]
                    elif links_map.has_key(path[l - 1]):
                        a = path[l - 1]
                        links_map[a][path[l]] = self.max_capacity - link['bandwidth']
                        b = path[l]
                    else:
                        links_map[path[l]] = {}
                        a = path[l]
                        links_map[a][path[l - 1]] = self.max_capacity - link['bandwidth']
                        b = path[l - 1]

                # Update current link bandwidth
                links_map[a][b] += demand['size']

                # Calculates link utilization
                new_link_utilization = float(links_map[a][b])

                max_link_utilization = max(new_link_utilization, max_link_utilization)

        return max_link_utilization / self.max_capacity

