"""
algorithms/operators.py
Defines candidate neighborhood generation and genetic recombination operators.
"""

from typing import List,Iterator,Set,Tuple
from core.state import State
from core.problem import CommuteProblem
import random

# max number of edges in a detour (used only by the multi-node detour move)
MAX_DETOUR_HOPS = 4


def cal_new_time(state: State, step, min_time, max_time) -> List[float]:
    times = []

    if(min_time <= state.departure_time + step  <= max_time):
        times.append(state.departure_time + step)

    if(min_time <= state.departure_time - step  <= max_time):
        times.append(state.departure_time - step)

    return times


def find_alternative_subpaths(problem: CommuteProblem, src: str, dst: str, banned: set, max_hops: int):
    stack = [(src, (src,))]
    while stack:
        node, p = stack.pop()
        if len(p) - 1 >= max_hops:
            continue
        for nxt in problem.network.get_neighbors(node):
            if nxt in banned or nxt in p:
                continue
            if nxt == dst:
                yield p + (nxt,)
            else:
                stack.append((nxt, p + (nxt,)))


def get_neighbors(state: State, problem: CommuteProblem) -> List[State]:
    neighbors = []
 
    # different start_time
    for new_time in cal_new_time(state, problem.t_step, problem.t_min, problem.t_max):
        new_time_state = State(path=state.path, departure_time=new_time)
        if problem.is_valid_state(new_time_state):
            neighbors.append(new_time_state)
 
 
    # different path(replacing)
    for i in range(1, len(state.path)-1):
        prev_node = state.path[i-1]
        next_node = state.path[i+1]
        available_nodes = problem.network.get_neighbors(prev_node)
        for new_node in available_nodes:
            if new_node in state.path:
                continue
            if problem.network.has_edge(new_node, next_node):
                new_path = state.path[:i] + (new_node,) + state.path[i+1:]
                new_path_state = State(path= new_path, departure_time= state.departure_time)
                if problem.is_valid_state(new_path_state):
                    neighbors.append(new_path_state)
 
                    ## different time and path
                    for new_time in cal_new_time(state, problem.t_step, problem.t_min, problem.t_max):
                        new_path_and_time_state = State(path=new_path, departure_time=new_time)
                        if problem.is_valid_state(new_path_and_time_state):
                            neighbors.append(new_path_and_time_state)
 
 
 
    # different path(removing)
    for i in range(1, len(state.path) - 1):
        prev_node = state.path[i-1]
        next_node = state.path[i+1]
        if problem.network.has_edge(prev_node, next_node):
            new_path = state.path[:i] + state.path[i + 1:]
            new_path_state = State(path=new_path, departure_time=state.departure_time)
            if problem.is_valid_state(new_path_state):
                neighbors.append(new_path_state)
 
                ## different time and path
                for new_time in cal_new_time(state, problem.t_step, problem.t_min, problem.t_max):
                    new_path_and_time_state = State(path=new_path, departure_time=new_time)
                    if problem.is_valid_state(new_path_and_time_state):
                        neighbors.append(new_path_and_time_state)
 
 
 
    # different path(inserting)
    for i in range(len(state.path) - 1):
        u = state.path[i]
        v = state.path[i+1]
        for new_node in problem.network.get_neighbors(u):
            if new_node in state.path:
                continue
            if problem.network.has_edge(new_node, v):
                new_path = state.path[:i + 1] + (new_node,) + state.path[i + 1:]
                new_path_state = State(path=new_path, departure_time=state.departure_time)
                if problem.is_valid_state(new_path_state):
                    neighbors.append(new_path_state)
 
                    ## different time and path
                    for new_time in cal_new_time(state, problem.t_step,problem.t_min, problem.t_max):
                        new_path_and_time_state = State(path=new_path, departure_time=new_time)
                        if problem.is_valid_state(new_path_and_time_state):
                            neighbors.append(new_path_and_time_state)
 
 
    # different path(detour: replacing a sub-path with 2 or more inner nodes)
    # the moves above only change one node at a time, this one can change several at once
    seen = set(neighbors)
    seen.add(state)
    times = cal_new_time(state, problem.t_step, problem.t_min, problem.t_max)
    for i in range(len(state.path) - 1):
        for j in range(i + 3, min(len(state.path), i + MAX_DETOUR_HOPS + 1)):
            banned = set(state.path[:i]) | set(state.path[j + 1:])
            for sub in find_alternative_subpaths(problem, state.path[i], state.path[j], banned, MAX_DETOUR_HOPS):
                new_path = state.path[:i] + sub + state.path[j + 1:]
                new_path_state = State(path=new_path, departure_time=state.departure_time)
                if new_path_state in seen:
                    continue
                seen.add(new_path_state)
                if problem.is_valid_state(new_path_state):
                    neighbors.append(new_path_state)
 
                    ## different time and path
                    for new_time in times:
                        new_path_and_time_state = State(path=new_path, departure_time=new_time)
                        if new_path_and_time_state in seen:
                            continue
                        seen.add(new_path_and_time_state)
                        if problem.is_valid_state(new_path_and_time_state):
                            neighbors.append(new_path_and_time_state)
 
    return neighbors


def crossover(parent1: State, parent2: State, problem: CommuteProblem) -> State:
    internal_path1 = parent1.path[1:-1]
    internal_path2 = parent2.path[1:-1]
    common_nodes = set(internal_path1) & set(internal_path2)

    time = (parent1.departure_time + parent2.departure_time) / 2
    valid_times = problem.get_valid_time_domain()
    child_departure_time = min(valid_times, key=lambda t: abs(t - time))

    # collect every valid child path (prefix of one parent + suffix of the other)
    candidates = []
    for first, second in ((parent1, parent2), (parent2, parent1)):
        for node in first.path:
            if node not in common_nodes:
                continue
            new_path = tuple(first.path[:first.path.index(node) + 1] + second.path[second.path.index(node) + 1:])
            if new_path not in candidates and problem.is_valid_path(new_path):
                candidates.append(new_path)

    if candidates:
        return State(path=random.choice(candidates), departure_time=child_departure_time)

    # no common node works: keep a parent's path, but with the averaged time
    for parent in (parent1, parent2):
        if problem.is_valid_path(parent.path):
            return State(path=parent.path, departure_time=child_departure_time)

    # Generate a valid state if both parents are invalid
    return problem.generate_initial_state()