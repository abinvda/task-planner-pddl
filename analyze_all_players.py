# Note: Calls analyze_plan.py for each player data and save their performance, mistake count etc. in a file (one level , all players)

from __future__ import print_function
from analyze_plan import analyze_plan
from utils import *


if __name__ == '__main__':
    dirname = path.dirname(__file__)

    for file_name in os.listdir(dirname + '/Player_Data/Levels/')[3:4]:
        output_stream = {}
        output_stream['worker_data'] = []
        input_stream = read_json_file('Player_Data/Levels/' + file_name)
        output_stream['level'] = input_stream['level']
        for idx, solution in enumerate(input_stream['solutions']):
            print(input_stream['level'], "  ", idx)
            worker_data = {}
            cost_to_go, CTG_increase_count, CTG_stays_same, freeze_probe_data, Q_value_data = analyze_plan(solution, input_stream['level'])
            worker_data['worker_name'] = solution['worker_name']
            worker_data['players_plan_length'] = len(solution['plan'])
            worker_data['cost_to_go'] = cost_to_go
            worker_data['CTG_increase_count'] = CTG_increase_count
            worker_data['CTG_stays_same'] = CTG_stays_same
            worker_data['Q_value_data'] = Q_value_data
            reverse_mode = 1  # FIXME: Check what this reverse mode is doing here.
            if reverse_mode:
                try:  # TODO: Only in case of reverse mode
                    freeze_probe_data['mistake_so_far'] = CTG_increase_count - freeze_probe_data['mistake_so_far']
                    freeze_probe_data['redundant_so_far'] = CTG_stays_same - freeze_probe_data['redundant_so_far']
                except KeyError:
                    pass
            else:
                pass
            worker_data['freeze_probe_data'] = freeze_probe_data
            output_stream['worker_data'].append(worker_data)

            from_planner_to_shared_format(output_stream, 'Player_Data/Level_Analysis/Analysis_' + file_name)
        t=1