import sys
import matplotlib.pyplot as plt
import numpy as np
import random
import time
import os
import math
import csv
import copy
import gc

list_of_cities=[]
mutate_prob = 0.3
tournament_size = 7
elitism = True
print_route = True

class City(object):
    def __init__(self, index, xy):
        self.index = index
        self.xy = xy

    def calculate_distance(self, city):
        return self.point_dist(self.xy, city.xy)

    def point_dist(self, xy1, xy2):
        return np.linalg.norm(xy1-xy2, 2, 0)

class Route(object):
    def __init__(self, make=False):
        if make:
            self.route = self.make_init()
        else:
            self.route = self.random_init()
        self.recalc_rt_len()

    def recalc_rt_len(self):
        self.length = 0.0

        for i in range(0, len(self.route)-1):
            next_city = self.route[i+1]
            dist_to_next = self.route[i].calculate_distance(next_city)
            self.length += dist_to_next

    def print_cities_in_rt(self):
        cities_res = ''
        for city in self.route:
            cities_res += city.index + ','
        if cities_res[-1] == ',':
            cities_res = cities_res[:-1]
        if print_route:
            print(cities_res)

    def is_valid_route(self):
        for city in list_of_cities:
            if self.count_mult(self.route, lambda c: c.index == city.index) > 1:
                return False
        return True

    def count_mult(self, seq, pred):
        return sum(1 for v in seq if pred(v))

    def tsp_2opt(self):
        k = random.randint(0, len(list_of_cities) - 1)
        d = list_of_cities[:]
        n = [list_of_cities[k]]
        d.pop(k)

        while len(d) > 0:
            min_dist = 1e10
            idx = -1
            for (i, j) in enumerate(d):
                new_dist = j.calculate_distance(n[-1])
                if new_dist < min_dist:
                    min_dist, idx = new_dist, i
            n.append(d[idx])
            d.pop(idx)
        return n

    def random_init(self):
        return sorted(list_of_cities, key=lambda *args: random.random())

    def make_init(self):
        return self.tsp_2opt()

class RoutePop(object):
    def __init__(self, size, initialize, make_Route=False):
        self.rt_pop = []
        self.size = size
        if initialize:
            for i in range(size):
                new_rt = Route(make_Route)
                self.rt_pop.append(new_rt)
            self.get_fittest()

    def get_fittest(self):
        sorted_list = sorted(self.rt_pop, key=lambda x: x.length, reverse=False)
        self.fittest = sorted_list[0]
        return self.fittest

    def get_lengths(self):
        sorted_list = sorted(self.rt_pop, key=lambda x: x.length, reverse=False)
        length_list = [r.length for r in sorted_list]
        return length_list

class GA(object):
    def crossover_experimental(self, parent1, parent2):
        child_rt = Route()
        rtB_len = len(routeB.route)
        random_city = random.choice(list_of_cities)

    def crossover(self, parent1, parent2):
        child_rt = Route()

        for i in range(len(child_rt.route)):
            child_rt.route[i] = None

        start_pos = random.randint(0, len(parent1.route))
        end_pos = random.randint(0, len(parent2.route))
        if start_pos < end_pos:
            for i in range(start_pos, end_pos):
                child_rt.route[i] = parent1.route[i]
        elif start_pos > end_pos:
            for i in range(end_pos, start_pos):
                child_rt.route[i] = parent1.route[i]

        for i in range(len(parent2.route)):
            if not parent2.route[i] in child_rt.route:
                for j in range(len(child_rt.route)):
                    if child_rt.route[j] == None:
                        child_rt.route[j] = parent2.route[i]
                        break

        child_rt.recalc_rt_len()
        return child_rt

    def mutate(self, route_to_mut):
        if random.random() < mutate_prob:
            mut_pos1 = random.randint(0, len(route_to_mut.route) - 1)
            mut_pos2 = random.randint(0, len(route_to_mut.route) - 1)

            if mut_pos1 == mut_pos2:
                return route_to_mut

            city1 = route_to_mut.route[mut_pos1]
            city2 = route_to_mut.route[mut_pos2]

            route_to_mut.route[mut_pos2] = city1
            route_to_mut.route[mut_pos1] = city2

        route_to_mut.recalc_rt_len()

        return route_to_mut

    def tournament_select(self, population):
        tournament_pop = RoutePop(size=tournament_size, initialize=False)

        for i in range(tournament_size-1):
            tournament_pop.rt_pop.append(random.choice(population.rt_pop))

        return tournament_pop.get_fittest()

    def evolve_population(self, init_pop):
        descendant_pop = RoutePop(size=init_pop.size, initialize=True)

        elitismOffset = 0

        if elitism:
            descendant_pop.rt_pop[0] = init_pop.fittest
            elitismOffset = 1

        for i in range(elitismOffset, descendant_pop.size):
            tournament_parent1 = self.tournament_select(init_pop)
            tournament_parent2 = self.tournament_select(init_pop)

            tournament_child = self.crossover(tournament_parent1, tournament_parent2)

            descendant_pop.rt_pop[i] = tournament_child

        for route in descendant_pop.rt_pop:
            if random.random() < mutate_prob:
                self.mutate(route)

        descendant_pop.get_fittest()

        return descendant_pop

class App(object):
    def __init__(self, n_generations, pop_size):
        self.n_generations = n_generations
        self.pop_size = pop_size
        print("GA_loop")
        self.GA_loop(n_generations, pop_size)

    def GA_loop(self, n_generations, pop_size):
        start_time = time.time()

        print("Create Populations Start")
        the_population = RoutePop(pop_size, True, True)
        print("Create Populations End")

        if the_population.fittest.is_valid_route() == False:
            raise NameError("multiple cities with same index")
            return

        initial_length = the_population.fittest.length
        best_route = Route()

        for i in range(1, n_generations+1):
            the_population = GA().evolve_population(the_population)

            if the_population.fittest.length < best_route.length:
                best_route = copy.deepcopy(the_population.fittest)

            #self.clear_term()
            print('Generation {0} of {1}'.format(i,n_generations))
            print(' ')
            print('Overall fittest has length {0:.2f}'.format(best_route.length))
            print('and goes via:')
            best_route.print_cities_in_rt()
            print(' ')
            print('Current fittest has length {0:.2f}'.format(the_population.fittest.length))
            print('And goes via:')
            the_population.fittest.print_cities_in_rt()
            print(the_population.get_lengths())

            print(' ')

    def clear_term(self):
        os.system('cls' if os.name=='nt' else 'clear')

def file_open(file):
    i=0
    f = open(file, 'r')
    lines = f.readlines()
    index = lines.index('NODE_COORD_SECTION\n')
    datas = lines[index+1:-1]

    for data in datas:
        l = data.split(' ')
        l[:] = [value.replace('\n', '') for value in l if value != '']
        city = City(l[0], np.array([float(l[1]), float(l[2])]))
        list_of_cities.append(city)

file_open('ali535.tsp')
app = App(n_generations=10, pop_size=100)
