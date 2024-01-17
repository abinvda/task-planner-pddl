#!/usr/bin/env python

from __future__ import print_function
from utils import *

dirname = path.dirname(__file__)


if __name__ == '__main__':

    filename = "config_B5_C14_P2_D1_19.json"  # config_B5_C14_P2_D1_20  # "config_B4_C12_P2_D1_46.json"   # "config_B3_C8_P2_D1_84.json"
    print(filename)

    input_stream = read_json_file("problem_config_files/" + filename)

    objects, compCount, boxes_order, compTarget, compTarget2, nDisplay, nPlatforms = parse_shared_file(input_stream)

    domain = get_domain(nDisplay)

    init = get_init(objects, compCount, boxes_order, nPlatforms, nDisplay)
    goal = get_goal(objects, nPlatforms, compTarget)

    static_literals = get_static_literals(objects['container'], objects['component'])
    precedence = get_precedence()

    problem = Problem(domain, objects, static_literals, init, goal, precedence)
    total_heuristic = get_heuristic(problem, compTarget2, objects)

    # GET saved list of optimal actions for some states
    try:
        optimal_actions = read_object("problem_config_files/optimal_actions_" + filename)  # , problem.grounded_actions)
    except:
        print('Optimal_actions file not found. Will create a new one.')
        optimal_actions = defaultdict(set)

    planner_output = planner(problem, heuristic=total_heuristic, verbose=True, nPlans=1, optimal_actions=optimal_actions)

    if planner_output is None:
        print('No Plan!')
    else:
        db_changed = 0
        for plans in planner_output:
            actions, states, states_explored = plans
            for i in range(len(actions)):
                print(actions[i], '--> CTG:', len(actions)-i-1, '--> H:', total_heuristic(states[i + 1]))
            print('\n')
        optimal_actions, db_change = update_optimal_actions_data(optimal_actions, planner_output)
        db_changed = db_changed or db_change

        if db_changed:
            save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)

    optimal_path = planner_output[0][1]  # It is the list of states that the optimal path goes through
    children_nodes = get_children_nodes(optimal_path, problem, total_heuristic, itr=1, max_nodes=1000)
    counter = len(children_nodes)
    try:
        db_changed = 0
        for node in children_nodes:
            counter -= 1
            problem.set_initial_state(node)

            planner_output = planner(problem, heuristic=total_heuristic, verbose=True, nPlans=1,
                                     optimal_actions=optimal_actions)

            if planner_output is None:
                print('No Plan!')
            else:
                optimal_actions, db_change = update_optimal_actions_data(optimal_actions, planner_output)
                db_changed = db_changed or db_change

            if db_changed and counter % 7 == 0:
                save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)
                db_changed = 0
        save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)
    except KeyboardInterrupt:
        save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)
    t=1



