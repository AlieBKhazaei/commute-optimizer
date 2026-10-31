"""
algorithms/genetic_algorithm.py
Population-based optimization using selection, recombination, and mutation.
"""

from typing import Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors, crossover
import random


class GeneticAlgorithmSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.population_size: int = self.params.get("population_size", 30)
        self.generations: int = self.params.get("generations", 100)
        self.crossover_rate: float = self.params.get("crossover_rate", 0.8)
        self.mutation_rate: float = self.params.get("mutation_rate", 0.2)
        self.elitism: int = self.params.get("elitism", 2)
        self.tournament_size: int = self.params.get("tournament_size", 3)
 
    def solve(self) -> Tuple[State, float]:
        self.history = []
 
        # first population: the initial state + random states
        # (random departure time + random steps on the neighbors)
        population = [self.problem.generate_initial_state()]
        while len(population) < self.population_size :
            base_state = self.problem.generate_initial_state()
            state = State(path=base_state.path,
                          departure_time=random.choice(self.problem.get_valid_time_domain()))
            max_steps = random.randint(0, 10)
            steps = 0
            while steps < max_steps :
                steps += 1
                neighbors = get_neighbors(state, self.problem)
                if not neighbors:
                    break
                state = random.choice(neighbors)
            population.append(state)
 
        best_state = population[0]
        best_cost = self.problem.evaluate(best_state)
 
        generation = 0
        while generation < self.generations :
            generation += 1
 
            # best states first
            population.sort(key=self.problem.evaluate)
            top_cost = self.problem.evaluate(population[0])
            if top_cost < best_cost:
                best_state = population[0]
                best_cost = top_cost
            self.history.append(best_cost)
 
            # elitism: the best states go to the next generation without change
            new_population = population[:self.elitism]
 
            while len(new_population) < self.population_size :
                # choose 2 parents with tournament selection
                # fitness = 1 / (1 + cost)  -> lower cost, higher fitness
                parents = []
                while len(parents) < 2 :
                    winner = random.choice(population)
                    winner_fitness = 1.0 / (1.0 + self.problem.evaluate(winner))
                    count = 1
                    while count < self.tournament_size :
                        count += 1
                        contender = random.choice(population)
                        contender_fitness = 1.0 / (1.0 + self.problem.evaluate(contender))
                        if contender_fitness > winner_fitness:
                            winner = contender
                            winner_fitness = contender_fitness
                    parents.append(winner)
                parent1 = parents[0]
                parent2 = parents[1]
 
                # crossover
                if random.random() < self.crossover_rate:
                    child = crossover(parent1, parent2, self.problem)
                else:
                    child = parent1
 
                # mutation: go to a random neighbor (different time or detour)
                if random.random() < self.mutation_rate:
                    neighbors = get_neighbors(child, self.problem)
                    if neighbors:
                        child = random.choice(neighbors)
 
                new_population.append(child)
 
            population = new_population
 
        # check the last generation too
        for state in population:
            cost = self.problem.evaluate(state)
            if cost < best_cost:
                best_state = state
                best_cost = cost
        self.history.append(best_cost)
 
        return(best_state, best_cost)
