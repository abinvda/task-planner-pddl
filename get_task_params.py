from __future__ import print_function
from utils import *
from solve_from_shared_format import solve_from_shared_format

if __name__ == '__main__':
    levels = ["config_B3_C8_P2_D1_84.json", "config_B3_C8_P3_D2_97.json", "config_B3_C8_P2_D1_9.json",
              "config_B4_C12_P3_D2_69.json", "config_B4_C12_P2_D1_29.json", "config_B4_C12_P2_D1_46.json",
              "config_B5_C14_P2_D1_20.json", "config_B5_C14_P2_D1_19.json", "config_B5_C14_P3_D2_17.json", ]
    output_stream = []
    for level in levels:
        level_info = {}
        level_info['level_name'] = level
        # try:
        #     optimal_actions = read_object("problem_config_files/optimal_actions_" + level)  # , problem.grounded_actions)
        # except:
        #     print('Optimal_actions file not found.')
        optimal_actions = defaultdict(set)

        planner_output = solve_from_shared_format(level, optimal_actions, verbose=0)

        optimal_path = planner_output[0][0][1]
        level_info['branching_factor'] = get_branching_factor(optimal_path, planner_output[1])
        level_info['StatesExplored'] = planner_output[0][0][2]  # states_explored
        output_stream.append(level_info)
    from_planner_to_shared_format(output_stream, "problem_config_files/level_info.json")
