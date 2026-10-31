"""
algorithms/hill_climbing.py
Hill Climbing search with sideways move limits and random restarts.
"""
 
import random
from typing import Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors
 
 
class HillClimbingSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.max_sideways: int = self.params.get("max_sideways", 100)   # باید از حالتی که حرکت افقی نتونه بکنه رو هم پشتیبانی کنه؟
        self.max_restarts: int = self.params.get("max_restarts", 5)
 
    def random_start(self) -> State:
        base = self.problem.generate_initial_state()
        state = State(path=base.path,
                      departure_time=random.choice(self.problem.get_valid_time_domain()))
        for _ in range(10):
            neighbors = get_neighbors(state, self.problem)
            if not neighbors:
                break
            state = random.choice(neighbors)
        return state
 
    def climb(self, current_state: State) -> Tuple[State, float]:
        current_cost = self.problem.evaluate(current_state)
        self.history.append(current_cost)
        neighbors = get_neighbors(current_state, self.problem)
        if not neighbors:
            return(current_state, current_cost)
        else:
            next_state = min(neighbors, key=self.problem.evaluate)
            next_cost = self.problem.evaluate(next_state)
 
        count_sideway = 0
        while current_cost >= next_cost :
            while current_cost == next_cost and count_sideway < self.max_sideways :
                count_sideway += 1
                current_state = next_state
                current_cost = next_cost
                self.history.append(current_cost)
                neighbors = get_neighbors(current_state, self.problem)
                if not neighbors:
                    return(current_state, current_cost)
                else:
                    next_state = min(neighbors, key=self.problem.evaluate)
                    next_cost = self.problem.evaluate(next_state)
 
                if count_sideway == self.max_sideways :
                    break
 
            if current_cost == next_cost and count_sideway == self.max_sideways :
                break
            elif current_cost > next_cost :
                count_sideway = 0
                current_state = next_state
                current_cost = next_cost
                self.history.append(current_cost)
                neighbors = get_neighbors(current_state, self.problem)
                if not neighbors:
                    return(current_state, current_cost)
                else:
                    next_state = min(neighbors, key=self.problem.evaluate)
                    next_cost = self.problem.evaluate(next_state)
            else :
                return(current_state, current_cost)
 
        # reached when the loop ends (local optimum, or sideways limit hit)
        return(current_state, current_cost)
 
    def solve(self) -> Tuple[State, float]:
        self.history = []
        best_state, best_cost = self.climb(self.problem.generate_initial_state())
        for _ in range(self.max_restarts):
            state, cost = self.climb(self.random_start())
            if cost < best_cost:
                best_state, best_cost = state, cost
 
        return(best_state, best_cost)