"""
algorithms/hill_climbing.py
Hill Climbing search with sideways move limits and random restarts.
"""

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

    def solve(self) -> Tuple[State, float]:
        self.history = []
        current_state = self.problem.generate_initial_state()
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
 
