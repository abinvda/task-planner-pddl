from __future__ import print_function
from time import time, clock
import heapq
import random
from collections import defaultdict


# from multiprocessing import Pool
# from random import randint
# import pyddl
# from pyddl import listit
def bidirectional_planner(problem, heuristic=None, state0=None, goal=None,
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
    heuristic_F = heuristic[0]  # expected CTG from given state to goal
    heuristic_R = heuristic[1]  # expected CTG from given state to initial state
    if not heuristic_F:
        heuristic_F = null_heuristic
    if not heuristic_R:
        heuristic_R = null_heuristic
    if not state0:
        state0 = problem.initial_state

    pos_goals = []
    neg_goals = []
    for literal in problem.goals:
        if literal[0] == 'not':
            neg_goals.append(literal[1])
        else:
            pos_goals.append(literal)
    goal_F = pos_goals, neg_goals, problem.num_goals

    goal_state = problem.goal_state  # for now assuming there's only one goal state

    states_explored = 0
    closed_F = set()
    closed_R = set()
    visited_F = set()
    visited_R = set()

    fringe_F = [(heuristic_F(state0), -state0.cost, state0)]  # forward open list
    heapq.heapify(fringe_F)
    visited_F.add(state0)

    fringe_R = [(heuristic_R(goal_state), -0, goal_state)]  # reverse open list
    heapq.heapify(fringe_R)
    visited_R.add(goal_state)

    start = time()
    optimal_plan_len = [999, ]
    plans = []
    current_max = 0

    while len(fringe_R) and len(fringe_F):
        if len(fringe_F):  # if forward open list is not empty  # But why is it needed, already in while loop
            h, _, node = heapq.heappop(fringe_F)
            states_explored += 1
            if node in visited_R:  # or node.is_true(*goal_F):  # TODO: but check if it should be only closed or closed+fringe
                print('Success')  # closed and fringe together depicts the visited nodes
                dur = time() - start
                temp = list(visited_R)
                node_r = temp[temp.index(node)]
                temp = None
                node_f = node
                plan = [node_f.plan()[0] + ['join'] + node_r.plan_R(problem)[0], node_f.plan()[1] + node_r.plan_R(problem)[1]]  # TODO: Optimize this line.  # Plan from start to that node and from there to the goal
                if verbose:
                    print('Plan found.')
                    print('States Explored: %d' % states_explored)
                    print('Total time: %.4f sec' % dur)
                    print('Time per state: %.4f ms' % (1000 * dur / states_explored))
                    print('Plan length: %d' % len(plan[0]))
                if len(plan[0]) > 26:
                    continue
                return [plan[0], plan[1], states_explored]  # , fringe  # , optimal_actions

            if node not in closed_F:
                closed_F.add(node)

                # Apply all applicable actions to get successors
                successors = set(
                    node.apply(action, monotone) for action in problem.grounded_actions if node.is_applicable(action))
                # Compute heuristic and add to fringe
                for successor in successors:
                    if successor not in closed_F:  # closed_F:  # TODO: closed or visited?
                        f = successor.cost + heuristic_F(successor)
                        heapq.heappush(fringe_F, (f, -successor.cost, successor))
                        visited_F.add(successor)
                    # else:
                    #     temp = list(visited_F)
                    #     successor_from_visited = temp[temp.index(successor)]
                    #     if successor.cost < successor_from_visited.cost:
                    #         visited_F.remove(successor_from_visited)
                    #         visited_F.add(successor)
                    #     temp = None

        if len(fringe_R):  # if reverse open list is not empty
            h, _, node = heapq.heappop(fringe_R)
            # visited_R.add(node)
            states_explored += 1
            if node in visited_F:
                print('Success')
                dur = time() - start
                temp = list(visited_F)
                node_f = temp[temp.index(node)]
                temp = None
                node_r = node
                plan = [node_f.plan()[0] + ['join'] + node_r.plan_R(problem)[0], node_f.plan()[1] + node_r.plan_R(problem)[1]]
                if verbose:
                    print('Plan found.')
                    print('States Explored: %d' % states_explored)
                    print('Total time: %.4f sec' % dur)
                    print('Time per state: %.4f ms' % (1000 * dur / states_explored))
                    print('Plan length: %d' % len(plan[0]))
                if len(plan[0]) > 45:
                    continue
                return [plan[0], plan[1], states_explored]

            if node not in closed_R:
                closed_R.add(node)
                # Apply all applicable actions to get successors
                successors = set(node.apply(action) for action in problem.grounded_actions if node.is_applicable(action))
                # Compute heuristic and add to fringe
                for successor in successors:
                    if successor not in visited_R:  # closed_R:
                        f = successor.cost + heuristic_R(successor)
                        visited_R.add(successor)
                        heapq.heappush(fringe_R, (f, -successor.cost, successor))
                    # else:
                    #     temp = list(visited_R)
                    #     successor_from_visited = temp[temp.index(successor)]
                    #     if successor.cost < successor_from_visited.cost:
                    #         visited_R.remove(successor_from_visited)
                    #         visited_R.add(successor)
                    #     temp = None

    print('This means failure!!')
    dur = time() - start
    # failed_plan = node.plan()
    if verbose:
        print('No Plan!!!')
        print('States Explored: %d' % states_explored)
        print('Total time: %.3f sec' % dur)
    return [None, 0, states_explored]


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
