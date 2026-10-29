"""
algorithms/operators.py
Defines candidate neighborhood generation and genetic recombination operators.
"""

from typing import List
from core.state import State
from core.problem import CommuteProblem


def cal_new_time(state: State, step, min_time, max_time) -> List[float]:
    times = []

    if(min_time <= state.departure_time + step  <= max_time):
        times.append(state.departure_time + step)

    if(min_time <= state.departure_time - step  <= max_time):
        times.append(state.departure_time - step)

    return times



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

    return neighbors



def crossover(parent1: State, parent2: State, problem: CommuteProblem) -> State:
    internal_path1 = parent1.path[1:-1]
    internal_path2 = parent2.path[1:-1]
    common_nodes = set(internal_path1) & set(internal_path2)

    time = (parent1.departure_time + parent2.departure_time) / 2
    valid_times = problem.get_valid_time_domain()
    child_departure_time = min(valid_times, key=lambda t: abs(t - time))

    for node in parent1.path:
        if node not in common_nodes:
            continue
        new_path = tuple(parent1.path[:parent1.path.index(node) + 1] + parent2.path[parent2.path.index(node) + 1:])
        if problem.is_valid_path(new_path):
            child = State(path= new_path, departure_time= child_departure_time)
            if problem.is_valid_state(child):
                return child
            
    if problem.is_valid_state(parent1):
        return parent1

    if problem.is_valid_state(parent2):
        return parent2

    # Generate a valid state if both parents are invalid
    return problem.generate_initial_state()