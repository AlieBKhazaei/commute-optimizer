"""
algorithms/beam_search.py
Local Beam Search maintaining K parallel candidate states.
"""

from typing import Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors
import random


class LocalBeamSearchSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.beam_width: int = self.params.get("beam_width", 5)
        self.max_iterations: int = self.params.get("max_iterations", 150)


    def random_start(self) -> State:
        """Random departure time from the valid domain + a short random walk on the path."""
        base = self.problem.generate_initial_state()
        state = State(path=base.path,
                      departure_time=random.choice(self.problem.get_valid_time_domain()))
        for _ in range(10):
            neighbors = get_neighbors(state, self.problem)
            if not neighbors:
                break
            state = random.choice(neighbors)
        return state
 
    def solve(self) -> Tuple[State, float]:
        self.history = []
 
        # first beam: the initial state + different random states
        initial_state = self.problem.generate_initial_state()
        beam = [initial_state]
        visited = [initial_state]
        attempts = 0
        while len(beam) < self.beam_width and attempts < 10 * self.beam_width :
            attempts += 1
            start_state = self.random_start()
            if start_state not in visited:
                visited.append(start_state)
                beam.append(start_state)
 
        best_state = beam[0]
        best_cost = self.problem.evaluate(best_state)
        for state in beam:
            cost = self.problem.evaluate(state)
            if cost < best_cost:
                best_state = state
                best_cost = cost
        self.history.append(best_cost)
 
        iteration = 0
        improved = True
        while iteration < self.max_iterations and improved :
            iteration += 1
 
            # neighbors of all the states in the beam go to one pool
            pool = []
            for state in beam:
                neighbors = get_neighbors(state, self.problem)
                for neighbor in neighbors:
                    if neighbor not in visited and neighbor not in pool:
                        pool.append(neighbor)
            if not pool:
                break
 
            # best K states of the whole pool
            pool.sort(key=self.problem.evaluate)
            beam = pool[:self.beam_width]
            for state in beam:
                visited.append(state)
 
            top_cost = self.problem.evaluate(beam[0])
            if top_cost < best_cost:
                best_state = beam[0]
                best_cost = top_cost
            else:
                improved = False
 
            self.history.append(best_cost)
 
        return(best_state, best_cost)