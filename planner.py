from __future__ import print_function
from time import time, clock
import heapq
import random
from collections import defaultdict


# from multiprocessing import Pool
# from random import randint
# import pyddl
# from pyddl import listit
def planner(problem, heuristic=None, state0=None, goal=None,
            monotone=False, verbose=True, nPlans=1, optimal_actions={}, max_plan_len=9999):
    """
    Implements A* search to find a plan for the given problem.
    Arguments:
    problem   - a pyddl Problem
    heuristic - a heuristic to use (h(state) = 0 by default)
    state0    - initial state (problem.initial_state by default)
    goal      - tuple containing goal predicates and numerical conditions
                (default is (problem.goals, problem.num_goals))
    monotone  - if True, only applies actions by ignoring delete lists
    verbose   - if True, prints statistics before returning
    """
    if not heuristic:
        heuristic = null_heuristic
    if not state0:
        state0 = problem.initial_state
    if not goal:
        goal = problem.goals_as_a_list
    states_explored = 0
    closed = set()
    fringe = [(heuristic(state0), -state0.cost, state0)]
    heapq.heapify(fringe)
    start = time()
    optimal_plan_len = [999, ]
    plans = []
    current_max = 0
    while True:
        if not len(fringe):
            dur = time() - start
            # failed_plan = node.plan()
            if verbose:
                print('No Plan!!!')
                print('States Explored: %d' % states_explored)
                print('Total time: %.3f sec' % dur)
            return plans, optimal_actions  # [None, 0, states_explored]
        # Get node with minimum evaluation function from heap

        h, _, node = heapq.heappop(fringe)
        if _ > max_plan_len:
            print("expected plan length exceeded max plan length")
            return None
        states_explored += 1
        # Goal test
        if node.is_true(*goal):  # or (calculate_all_paths and (node in optimal_actions.keys())):  # Either goal is reached or we found a state whose optimal actions is already known
            plan = node.plan()
            # if len(plan[0]) <= min(optimal_plan_len) or (len(plan[0]) - min(optimal_plan_len) <= 3) :
            #     if optimal_plan_len[0] == 999:
            #         optimal_plan_len[0] = len(plan[0])
            #     else:
            #         optimal_plan_len.append(len(plan[0]))
            dur = time() - start
            if verbose:
                print('Plan found.')
                print('States Explored: %d' % states_explored)
                print('Total time: %.4f sec' % dur)
                print('Time per state: %.4f ms' % (1000 * dur / states_explored))
                print('Plan length: %d' % node.cost)
            plans.append([plan[0], plan[1], states_explored])
            if len(plans) >= nPlans:  # and calculate_all_paths:
                return plans  # , fringe  # , optimal_actions

        # Expand node if we haven't seen it before
        # t1 = time()
        if node in optimal_actions.keys():
            action = problem.grounded_actions_dict[random.sample(optimal_actions[node], 1)[0]]
            successor = node.apply(action)
            f = successor.cost + heuristic(successor) - 0.01  #TODO: Check if this can result in sub-optimality
            heapq.heappush(fringe, (f, -successor.cost, successor))
        else:
            if node not in closed:
                closed.add(node)

                # Apply all applicable actions to get successors
                successors = set(
                    node.apply(action) for action in problem.grounded_actions if (node.is_applicable(action) and node.apply(action) not in closed))

                # Compute heuristic and add to fringe
                [heapq.heappush(fringe, ((successor.cost + heuristic(successor)), -successor.cost, successor)) for
                 successor in successors]

                # for successor in successors:
                #     f = successor.cost + heuristic(successor)
                #     # if successor not in closed:
                #     heapq.heappush(fringe, (f, -successor.cost, successor))
        # print('f-value, processing time: ', h, ", ", (time() - t1))


########## HEURISTICS ##########
def null_heuristic(state):
    """Admissible, but trivial heuristic"""
    return 0


def plan_cost(plan):
    """Convert a plan to a cost, handling nonexistent plans"""
    if plan is None:
        return float('inf')
    else:
        return len(plan)


def monotone_heuristic(problem):
    """Heuristic that finds plans using only add lists of actions"""

    def h(state):
        monotone_plan = planner(problem, null_heuristic, state, monotone=True, verbose=False)
        return plan_cost(monotone_plan)

    return h


def subgoal_heuristic(problem):
    """Heuristic that computes the max cost of plans across all subgoals"""

    def h(state):
        costs = []
        for g in problem.goals:
            subgoal_plan = planner(problem, null_heuristic, state, ((g,), ()))
            costs.append(plan_cost(subgoal_plan))
        return max(costs)

    return h