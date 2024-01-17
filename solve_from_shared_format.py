#!/usr/bin/env python
# Takes in a problem configuration file in the common .json format and outputs the optimal plan, plan length, resource use and states explored.

from __future__ import print_function
from utils import *
from planner_rollout import planner_rollout


def solve_from_shared_format(filename, optimal_actions=defaultdict(set), verbose=0):
    collect()

    input_stream = read_json_file("problem_config_files/" + filename)

    objects, compCount, boxes_order, compTarget, compTarget2, nDisplay, nPlatforms = parse_shared_file(input_stream)

    domain = get_domain(nDisplay)

    init = get_init(objects, compCount, boxes_order, compTarget, nPlatforms, nDisplay)
    goal = get_goal(objects, nPlatforms, compTarget)

    static_literals = get_static_literals(objects['container'], objects['component'])
    precedence = get_precedence()

    problem = Problem(domain, objects, static_literals, init, goal, precedence)
    total_heuristic = get_heuristic(problem.goals, compTarget2, objects)

    # import random
    # state = problem.initial_state
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    # state = next_states[0]
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    # state = next_states[1]
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    # state = next_states[1]
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    # state = next_states[1]
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    # state = next_states[1]
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    # state = next_states[1]
    # next_states = list(state.apply(action) for action in problem.grounded_actions if state.is_applicable(action))
    #
    #
    # actual = []
    # estimate = []

    # for state in next_states:
    #     problem.set_initial_state(state)
    #     all_plans = planner(problem, heuristic=total_heuristic, verbose=True, optimal_actions=optimal_actions)
    #     actual.append(len(all_plans[0][0]))
    #     rollout_estimate = []
    #     for i in range(5):
    #         all_plans = planner_rollout(problem, heuristic=total_heuristic, verbose=True, optimal_actions=optimal_actions)
    #         rollout_estimate.append(len(all_plans[0][0]))
    #         for plans in all_plans:
    #             plan, states, states_explored = plans
    #             print('initial heuristic', '-->', total_heuristic(states[0]))
    #             for i in range(len(plan)):
    #                 print(plan[i], '-->', len(plan) - i - 1, '-', total_heuristic(states[i + 1]))
    #             print('\n')
    #     estimate.append(sum(rollout_estimate)/len(rollout_estimate))

    all_plans = planner(problem, heuristic=total_heuristic, verbose=True, optimal_actions=optimal_actions)
    if not verbose:
        return all_plans, problem, total_heuristic
    else:
        if all_plans is None:
            print('No Plan!')
        else:
            output_stream = input_stream
            for plans in all_plans:
                plan, states, states_explored = plans
                print('initial heuristic', '-->', total_heuristic(states[0]))
                for i in range(len(plan)):
                    print(plan[i], '-->', len(plan) - i - 1, '-', total_heuristic(states[i + 1]))
                print('\n')

                if plans == all_plans[0]:
                    output_stream['Plan'] = []
                    for i in range(len(plan)):
                        output_stream['Plan'].append(tuple(plan[i].sig))
                    output_stream['Plan_length'] = len(plan)

                    # Calculate redundancy
                    resource_use = {}
                    if states:
                        platforms = list(set(objects['box']) - set(objects['container']))
                        resource_use = get_resource_use(states[-1], platforms, objects['station'][0], nDisplay)

                    # Extra info
                    output_stream['ResourceUse'] = resource_use
                    output_stream['StatesExplored'] = states_explored
                    # output_stream['GridEntropy'] = entropy
                    from_planner_to_shared_format(output_stream, "problem_config_files/" + filename)


def solve_from_file_bidirectional(filename, optimal_actions=defaultdict(set), verbose=0):
    collect()

    input_stream = read_json_file("problem_config_files/" + filename)

    objects, compCount, boxes_order, compTarget, compTarget2, nDisplay, nPlatforms = parse_shared_file(input_stream)

    domain = get_domain(nDisplay)

    init, box_literals = get_init(objects, compCount, boxes_order, compTarget, nPlatforms, nDisplay, need_box_order=1)
    # TODO: make a separate function for box_literals based on objects[boxes]
    goal = get_goal(objects, nPlatforms, compTarget)

    goal_state = get_goal_state(objects, boxes_order, nPlatforms, nDisplay, compTarget, compCount)

    static_literals = get_static_literals(objects['container'], objects['component'])
    precedence = get_precedence()

    problem = Problem(domain, objects, static_literals, init, goal_state, precedence)

    component_init = defaultdict(list)
    # for k in compTarget2:
    #     for coords in compTarget2[k]:
    #         temp = list(map(lambda d: d * -1, coords))
    #         component_init[k].append(temp)

    # goal_f_dict = {}
    # for k, v in problem.initial_state.f_dict.items():
    #     goal_f_dict[k] = v
    # for k, v in goal_f_dict.items():
    #     if k[0] == 'onGrid':
    #         goal_f_dict[k] = goal_f_dict[('count', k[1])]
    # for k, v in goal_f_dict.items():
    #     if k[0] == 'visible' or k[0] == 'count':
    #         goal_f_dict[k] = 0

    # box_literals = [('top', 'box_cir', 'box_sqr'), ('top', 'box_sqr', 'box_tri'), ('top', 'box_tri', 'I'), ('clear', 'box_cir')]
    # goal_state = State(problem.goals+box_literals+[('blank', 3, 3)], goal_f_dict)
    heuristic_F = get_heuristic(problem.goals, compTarget2, objects)
    heuristic_R = get_reverse_heuristic(problem.goal_state, component_init, objects)
    total_heuristic = [heuristic_F, None]  # [heuristic_F, heuristic_R]

    all_plans = bidirectional_planner(problem, heuristic=total_heuristic, verbose=True, optimal_actions=optimal_actions, goal=goal_state)
    if not verbose:
        return all_plans, problem, total_heuristic
    else:
        if all_plans is None:
            print('No Plan!')
        else:
            output_stream = input_stream
            for plans in all_plans:
                plan, states, states_explored = plans
                print('initial heuristic', '-->', total_heuristic[0](states[0]), total_heuristic[1](states[0]))
                for i in range(len(plan)):
                    print(plan[i], '-->', len(plan) - i - 1, '-', total_heuristic[0](states[i + 1]), total_heuristic[1](states[i + 1]))
                print('\n')

                if plans == all_plans[0]:
                    output_stream['Plan'] = []
                    for i in range(len(plan)):
                        output_stream['Plan'].append(tuple(plan[i].sig))
                    output_stream['Plan_length'] = len(plan)

                    # Calculate redundancy
                    resource_use = {}
                    if states:
                        platforms = list(set(objects['box']) - set(objects['container']))
                        resource_use = get_resource_use(states[-1], platforms, objects['station'][0], nDisplay)

                    # Extra info
                    output_stream['ResourceUse'] = resource_use
                    output_stream['StatesExplored'] = states_explored
                    # output_stream['GridEntropy'] = entropy
                    from_planner_to_shared_format(output_stream, "problem_config_files/" + filename)


if __name__ == '__main__':
    '''from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)'''
    filename = "config_B4_C12_P2_D1_46.json"  # config_B5_C14_P2_D1_20  # "config_B4_C12_P2_D1_46.json"   # "config_B3_C8_P2_D1_84.json"  # config_B5_C14_P3_D2_17
    print(filename)
    # try:
    #     optimal_actions = read_object("problem_config_files/optimal_actions_" + filename)  # , problem.grounded_actions)
    # except:
    #     print('Optimal_actions file not found.')
    #     optimal_actions = defaultdict(set)

    # solve_from_file_bidirectional(filename, verbose=1)
    solve_from_shared_format(filename, verbose=1)