"""
algorithms/simulated_annealing.py
Stochastic optimization governed by a temperature schedule.
"""

from typing import Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors
import random
import math


class SimulatedAnnealingSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.initial_temp: float = self.params.get("initial_temp", 100.0)
        self.cooling_rate: float = self.params.get("cooling_rate", 0.995)
        self.min_temp: float = self.params.get("min_temp", 1e-3)
        self.max_iterations: int = self.params.get("max_iterations", 2000)

    def solve(self) -> Tuple[State, float]:
        self.history = []
        current_state = self.problem.generate_initial_state()
        current_cost = self.problem.evaluate(current_state)
        best_state = current_state
        best_cost = current_cost
        self.history.append(best_cost)
 
        temp = self.initial_temp
        iteration = 0
        while temp > self.min_temp and iteration < self.max_iterations :
            iteration += 1
            neighbors = get_neighbors(current_state, self.problem)
            if not neighbors:
                break
 
            # pick a random neighbor
            next_state = random.choice(neighbors)
            next_cost = self.problem.evaluate(next_state)
            delta_e = next_cost - current_cost
 
            # Metropolis criterion: better -> always accept, worse -> accept with P = exp(-dE/T)
            if delta_e < 0 or random.random() < math.exp(-delta_e / temp):
                current_state = next_state
                current_cost = next_cost
                if current_cost < best_cost:
                    best_state = current_state
                    best_cost = current_cost
 
            self.history.append(best_cost)
            temp = temp * self.cooling_rate   # T(k+1) = alpha * T(k)
 
        return(best_state, best_cost)