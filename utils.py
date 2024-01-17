# Contains all small functions and routines that are used in other files.

from __future__ import print_function

from planner import *
from bidirectional_planner import *
from get_domain import get_domain
from get_problem_config import *
from get_heuristics import *
import matplotlib.pyplot as plt
import numpy as np
import copy
from gc import collect
import json
import os
from os import environ, path
import dill as pickle

dirname = path.dirname(__file__)


def read_json_file(file_name):
    dirname = path.dirname(__file__)
    with open(os.path.join(dirname, file_name), 'r') as input_file:
        input_stream = json.load(input_file)
        return input_stream


def parse_shared_file(input_stream):
    objects = {}
    compCount = {}
    compTarget = {}
    compTarget2 = {}
    boxes_order = []

    objects['station'] = ('stat1',)
    objects['box'] = []
    objects['component'] = []

    objects['gridX'] = list(range(1, input_stream['GridSize']['x'] + 1))
    objects['gridY'] = list(range(1, input_stream['GridSize']['y'] + 1))

    for box in input_stream['Containers']:
        objects['box'].append(box['name'])
        boxes_order.append(box['name'])

        component = box['components'][0]  # TODO: If more than 1 type of component in a box then replace [0] with a loop that goes through box['components']
        objects['component'].append(component['name'])
        compCount[component['name']] = box['count']
        compTarget2[component['name']] = component['target']
        for target in component['target']:
            if not target[0] in compTarget.keys():
                compTarget[target[0]] = {}
            compTarget[target[0]][target[1]] = component['name']

    objects['box'] = tuple(objects['box'])
    objects['container'] = tuple(objects['box'])

    nPlatforms = input_stream['Platforms']
    platform_pool = ('I', 'II', 'III', 'IV')  # TODO: Should be a global variable
    platforms = platform_pool[:nPlatforms]
    objects['box'] = objects['box'] + platforms


    nDisplay = input_stream['Displays']
    nPlatforms = input_stream['Platforms']

    boxes_order = boxes_order[::-1]    ### Need to reverse the order to match with Pamela's format

    return objects, compCount, boxes_order, compTarget, compTarget2, nDisplay, nPlatforms


def save_object(objects, filename):
    with open(filename + '.pkl', 'wb') as f:
        pickle.dump(objects, f, pickle.DEFAULT_PROTOCOL)


def read_object(filename):
    with open(filename + '.pkl', 'rb') as f:
        return pickle.load(f)


def get_branching_factor(optimal_path, problem):
    # It will be the branching factor only 'along the optimal path'
    branching_factors = []
    for node in optimal_path:
        successors = list(node.apply(action) for action in problem.grounded_actions if node.is_applicable(action))
        branching_factors.append(len(successors)-2)  # -2 for error and redundant action
    return branching_factors


def get_children_nodes(optimal_path, problem, total_heuristic, itr=1, max_nodes=3000):
    children = optimal_path
    for i in range(itr):
        new_states = list()
        for node in children:
            what = total_heuristic
            successors = list(node.apply(action) for action in problem.grounded_actions if node.is_applicable(action))
            for successor in successors:
                if successor not in children:  # and successor not in optimal_actions
                    new_states.append(successor)
            if len(children) + len(new_states) > max_nodes:  # TODO: Check this condition
                break
        children.extend(new_states)
        if len(children) > max_nodes:
            break
    children.reverse()
    return children


def get_action_dict(problem):
    action_dict = {}
    for action in problem.grounded_actions:
        action_dict[action.sig] = action
    return action_dict


def simple_optimality_check(Problem, starting_state, end_state, idx):
    Problem.set_initial_state(starting_state)
    # Problem.set_goal_state(end_state)
    goals = []
    for g in end_state.predicates:
        goals.append(g)  # Not taking care of numerical goals
    new_heuristics = predicate_mismatch_heuristic(goals)
    planner_output = planner(Problem, goal=[goals, [], end_state.f_dict], heuristic=new_heuristics, verbose=False, max_plan_len=idx+1)
    steps_to_interm_state = len(planner_output[0][0])  # Steps to reach that intermediate state
    if steps_to_interm_state < idx:
        # Means the step was optimal
        return steps_to_interm_state, planner_output
    else:
        return None


def calculate_cost_to_go(problem, start_state, heuristics, optimal_actions, verbose=True):
    # try:
    #     if start_state not in optimal_actions:
    #         predecessor = start_state.predecessor[0]
    #         if predecessor in optimal_actions.keys():
    #             problem.set_initial_state(predecessor)
    #             Planner_output = planner(problem, heuristic=heuristics, verbose=False, optimal_actions=optimal_actions)
    #             This_CTG = len(Planner_output[0][0])
    #             following_states = Planner_output[0][1]
    #             following_states = following_states[0:min(len(following_states), max((len(following_states)//3), 12))]  # Only check for first portion
    #             for idx, each_state in enumerate(following_states):
    #                 each_state.predecessor = None
    #                 test_result = simple_optimality_check(problem, start_state, each_state, idx)
    #                 if test_result:
    #                     sub_CTG, planner_output = test_result
    #                     optimal_actions, db_changed = update_optimal_actions_data(optimal_actions, planner_output)
    #                     # db_changed = 0
    #                     print('current_CTG__: ', This_CTG-1)
    #                     return This_CTG-1, planner_output, optimal_actions, db_changed
    #                 else:
    #                     continue
    #             raise KeyError  # Means can't say about optimality, just that new optimal path doesn't merge with the current known one (within certain steps)
    #         else:
    #             raise KeyError
    #     else:
    #         raise KeyError
    #
    # except KeyError:
    problem.set_initial_state(start_state)
    planner_output = planner(problem, heuristic=heuristics, verbose=False, optimal_actions=optimal_actions)

    if not planner_output:
        print('No Plan!')
        return [[], None]
    else:
        if verbose:
            pass
            # print('current_CTG: ', len(planner_output[0][0]))
            # if len(planner_output[0][0]) != 0:
            #     print('Next best action: ', planner_output[0][0][0].sig)

        optimal_actions, db_changed = update_optimal_actions_data(optimal_actions, planner_output)

        return len(planner_output[0][0]), planner_output, optimal_actions, db_changed


def calculate_at_freeze_probe(problem, state, heuristics, optimal_actions):
    cost_to_go, planner_output, optimal_actions, db_changed = calculate_cost_to_go(problem, state, heuristics,
                                                                           optimal_actions)

    # Taking possible next actions from current state to determine next_best_action
    next_best_action = []
    next_states = set(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    for next_state in next_states:
        action = next_state.predecessor[1].sig
        ctg, planner_output, optimal_actions, db_change = calculate_cost_to_go(problem, next_state, heuristics, optimal_actions, verbose=False)
        db_changed = db_changed or db_change  # update if database has changed
        if ctg < cost_to_go:
            plan = planner_output[0][0]
            plan_labels = []
            for i in range(len(plan)):
                plan_labels.append(tuple(plan[i].sig))
            next_best_action.append([action] + plan_labels)

    return cost_to_go, planner_output, next_best_action, optimal_actions, db_changed


def get_all_Q_values(problem, state, heuristics, optimal_actions):
    Qsa = []
    next_states = set(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    db_changed = 0
    for next_state in next_states:
        action = next_state.predecessor[1].sig
        ctg, _, optimal_actions, db_changed = calculate_cost_to_go(problem, next_state, heuristics,
                                                                               optimal_actions, verbose=False)
        Qsa.append([action, ctg])

    return Qsa, optimal_actions, db_changed


def update_optimal_actions_data(optimal_actions, planner_output):
    db_changed = 0
    for plans in planner_output:
        actions, states, _ = plans
        for i in range(len(actions)):
            if states[i] not in optimal_actions.keys():
                db_changed = 1  # Flag to know if anything added to optimal_actions
                optimal_actions[states[i]].add(actions[i].sig)
    return optimal_actions, db_changed


def parse_players_plan(players_plan):
    container_names = {"box_sqr": 'ContainerBlueSquare', "box_tri": "ContainerGreenTriangle",
                       "box_cir": "ContainerRedCircle", "box_sqr_2": "ContainerYellowSquare",
                       "box_tri_2": "ContainerRedTriangle", "box_cir_2": "ContainerYellowCircle"
                       }
    component_names = {"square": "BlueSmallSquare", "triangle": "GreenSmallTriangle", "circle": "RedSmallCircle",
                       "square_2": "YellowSmallSquare", "triangle_2": "RedSmallTriangle",
                       "circle_2": "YellowSmallCircle"}

    platforms_names = {'Middle': 'II', 'Initial': 'I', 'Final': 'III'}
    component_names = dict(zip(component_names.values(), component_names.keys()))
    container_names = dict(zip(container_names.values(), container_names.keys()))
    new_names = {**container_names, **component_names, **platforms_names}

    action_list = []
    for action in players_plan:
        a = action['action'].split()
        action_name = a[0]
        parameters = [action_name]
        for param in a[1:]:
            if param in new_names:
                parameters.append(new_names[param])
            else:
                if param.isdigit():
                    parameters.append(int(param))
                else:
                    parameters.append(param)
        action_list.append(tuple(parameters))

    return action_list


def get_players_states(players_actions, problem):
    state = problem.initial_state
    players_states = [state]
    action_dict = get_action_dict(problem)
    for action_label in players_actions:
        try:
            action = action_dict[action_label]
            # print('Action taken: ', action_label)
            if state.is_applicable(action):
                state = state.apply(action)
                players_states.append(state)
            else:
                print('Invalid action in the list: ', action_label)
                break

        except KeyError:
            print('Unknown actions in the list: ', action_label)
    return players_states


def from_planner_to_shared_format(data, output_name):
    """
    Writes problem config and plan to json game format:
        Shared format is:
            platforms: #Total count
            display_locations: #Total count
            container_name: #num of components
                component_type: [position in grid]
    """
    with open(os.path.join(dirname, output_name), 'w') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=4)
        output_file.close()


def get_resource_use(state, platforms, station, nDisplay):
    n = 0
    resource_use = {}
    red_platform = 0
    red_display = 0

    platform_use = {station: 0}
    for platform in platforms:
        platform_use[platform] = 0

    display_use = {}
    for disp in range(0, nDisplay+1):
        display_use[disp] = 0

    while state.predecessor is not None:
        for platform in platforms:
            if ('clear', platform) in state.predicates:
                red_platform = red_platform + 1
            else:
                platform_use[platform] = platform_use[platform] + 1
        if ('clear', station) not in state.predicates:
            platform_use[station] = platform_use[station] + 1
        displayMax = [item[1] for item in state.functions if item[0] == 'displayMax']
        displayCurr = [item[1] for item in state.functions if item[0] == 'displayCurr']
        red_display = red_display + (displayMax[0] - displayCurr[0])
        display_use[displayCurr[0]] = display_use[displayCurr[0]] + 1
        state = state.predecessor[0]
        n = n + 1

    resource_use['Avg_redundancy'] = (red_display + red_platform)/n  # Average redundancy
    resource_use['PlatformUse'] = platform_use
    resource_use['DisplayUse'] = display_use
    return resource_use


def do_a_rollout(problem, beta, optimal_actions, total_heuristic):
    problema = copy.copy(problem)
    current_state = problema.initial_state
    action_dict = get_action_dict(problema)

    action_count = 0
    while not current_state.is_true(*problema.goals_as_a_list):
        Qsa, optimal_actions, _ = get_all_Q_values(problema, current_state, total_heuristic, optimal_actions)
        action_list = list()
        Q_value_list = list()
        for items in Qsa:
            action_list.append(items[0])
            Q_value_list.append((items[1]))
        action_probabilities = compute_boltzmann(beta, Q_value_list)
        # pick an action from action_list with probabilities given in action_probabilities
        choice = np.random.choice(len(action_list), p=action_probabilities)
        # apply that action
        current_state = current_state.apply(action_dict[action_list[choice]])
        action_count += 1
        # repeat
    return action_count, optimal_actions


def compute_boltzmann(beta, x):

    def f(value, temp):
        return np.exp(temp*value)  # removed the negative sign

    condpf = np.array([f(xi, beta) for xi in x if not np.isnan(xi)])
    condpf *= 1/sum(condpf)
    return condpf
