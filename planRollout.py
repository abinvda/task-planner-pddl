# Note: This file is to generate (simulate) a plan for a given beta value (skill). Multiple rollouts can be done for a single beta value and plan lenghts can be averaged to get mean plan lenght for that given beta.

from __future__ import print_function
from analyze_plan import analyze_plan
from solve_from_shared_format import *
from utils import *

if __name__ == '__main__':
    dirname = path.dirname(__file__)

    for file_name in os.listdir(dirname + '/Player_Data/Levels/')[3:4]:
        # Let beta comes as a dictionary with worker name as key and beta as value.
        beta_dict = read_json_file('Player_Data/Beta_Values/' + 'config_B3_C8_P3_D2_97_Plans.json')  # FIXME: change this once other beta values are there
        start_time = time()

        output_stream = {}
        output_stream['worker_data'] = []
        input_stream = read_json_file('Player_Data/Levels/' + file_name)
        output_stream['level'] = input_stream['level']
        level_name = input_stream['level'] + '.json'

        try:
            optimal_actions = read_object("problem_config_files/optimal_actions_" + level_name)
        except FileNotFoundError:
            print('Optimal_actions file not found.')
            optimal_actions = defaultdict(set)

        _, problem, total_heuristic = solve_from_shared_format(level_name, optimal_actions=optimal_actions)

        for idx, solution in enumerate(input_stream['solutions'][5:]):
            print(input_stream['level'], "  ", idx)
            worker_data = dict()
            worker_data['worker_name'] = solution['worker_name']
            worker_data['num_actions'] = beta_dict[solution['worker_name']]['num_actions']

            beta = beta_dict[solution['worker_name']]['estimated_beta']
            # beta = 15
            worker_data['estimated_beta'] = beta


            plan_lengths = list()
            for i in range(50):
                plan_length, optimal_actions = do_a_rollout(problem, beta, optimal_actions, total_heuristic)
                plan_lengths.append(plan_length)

            worker_data['estimated_num_actions'] = [np.mean(plan_lengths), np.std(plan_lengths)]
            # worker_data['rollout_plans'] = plan_lengths

            output_stream['worker_data'].append(worker_data)

            from_planner_to_shared_format(output_stream, 'Player_Data/Level_Rollouts/Rollout_' + file_name)

        save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)
        print('Total Time taken: ', time() - start_time)
        t = 1