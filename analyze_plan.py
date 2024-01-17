#!/usr/bin/env python
# This is: Takes in plan for a given level and returns cost-to-go, mistakes count etc.

from __future__ import print_function
from solve_from_shared_format import *
from utils import *

# dirname = path.dirname(__file__)


def analyze_plan(solution, level_name):
    level_name = level_name + '.json'
    freeze_probe_index = solution['freeze_probe_index']
    players_plan = solution['plan']

    start_time = time()
    try:
        optimal_actions = read_object("problem_config_files/optimal_actions_" + level_name)
    except FileNotFoundError:
        print('Optimal_actions file not found.')
        optimal_actions = defaultdict(set)

    planner_output, problem, total_heuristic = solve_from_shared_format(level_name, optimal_actions=optimal_actions)
    # planner_output, problem, total_heuristic = solve_from_file_bidirectional(level_name, optimal_actions=optimal_actions)

    db_changed = 0
    for plans in planner_output:
        actions, states, states_explored = plans
        for i in range(len(actions)):
            if states[i] not in optimal_actions.keys():
                db_changed = 1
                optimal_actions[states[i]].add(actions[i].sig)

    if db_changed:
        save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)

    plan = planner_output[0][0]
    initial_cost_to_go = len(plan)

    players_actions = parse_players_plan(players_plan)
    players_states = get_players_states(players_actions, problem)

    # This is: Q_value_data
    Q_value_data = defaultdict(list)
    for idx, player_state in enumerate(players_states):
        Q_value_data[idx], optimal_actions, db_change = get_all_Q_values(problem, player_state, total_heuristic, optimal_actions)
        db_changed = db_changed or db_change
        if db_changed:
            db_changed = 0
            save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)
    save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)


    freeze_probe_data = {}
    try:
        freeze_probe_state = players_states[freeze_probe_index + 1]  # +1 because probe is AFTER the action is played
        print('Freeze probe after action ', freeze_probe_index)
    except TypeError:
        freeze_probe_state = State([], {})
        print('No freeze probe in this level.')
    reverse_mode = 1
    if reverse_mode:
        players_states.reverse()
        players_actions.reverse()  # NOTE: The reverse mode. Planning from last action to first.

        cost_to_go = [-1]  # -1 for reverse 'initial_cost_to_go' for regular
        CTG_increase_count = 0
        CTG_stays_same = 0

        try:
            current_CTG = -1
            # for player_state, action_label in zip(players_states[1:], players_actions):  # player_states[0] is initial player_state
            for player_state in players_states:  # players_states[1:] for forward mode, players_states in reverse
                # player_state = players_states[i+1]
                # action_label = players_actions[i]
                # db_changed = 0
                if player_state == freeze_probe_state:
                    current_CTG, planner_output, next_best_action, optimal_actions, db_changed = calculate_at_freeze_probe(problem, player_state, total_heuristic, optimal_actions)
                    # TODO: In reverse mode, assign this current_CTG value before calling calculate_at_freeze_probe
                    freeze_probe_data['current_CTG'] = current_CTG
                    # TODO: Change to < if in reverse mode, > for regular mode
                    if current_CTG < cost_to_go[-1]:
                        CTG_increase_count += 1
                    if current_CTG == cost_to_go[-1]:
                        CTG_stays_same += 1
                    cost_to_go.append(current_CTG)
                    freeze_probe_data['mistake_so_far'] = CTG_increase_count
                    freeze_probe_data['redundant_so_far'] = CTG_stays_same
                    freeze_probe_data['next_best_action'] = next_best_action
                else:
                    current_CTG, planner_output, optimal_actions, db_changed = calculate_cost_to_go(problem, player_state, total_heuristic, optimal_actions)
                # print('Action taken: ', action_label)
                    # TODO: Change to < if in reverse mode
                    if current_CTG < cost_to_go[-1]:
                        CTG_increase_count += 1
                    if current_CTG == cost_to_go[-1]:
                        CTG_stays_same += 1
                    cost_to_go.append(current_CTG)

                if db_changed:
                    save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)  # TODO: See why it is taking so long.
        except KeyboardInterrupt:
            save_object(optimal_actions,
                        "problem_config_files/optimal_actions_" + level_name)  # TODO: See why it is taking so long.

        # save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)
        cost_to_go.pop(0)
        cost_to_go.reverse()

    else:
        cost_to_go = [initial_cost_to_go]  # -1 for reverse 'initial_cost_to_go' for regular
        CTG_increase_count = 0
        CTG_stays_same = 0

        try:
            current_CTG = -1
            # for player_state, action_label in zip(players_states[1:], players_actions):  # player_states[0] is initial player_state
            for player_state in players_states[1:]:  # players_states[1:] for forward mode, players_states in reverse
                # player_state = players_states[i+1]
                # action_label = players_actions[i]
                # db_changed = 0
                if player_state == freeze_probe_state:
                    current_CTG, planner_output, next_best_action, optimal_actions, db_changed = calculate_at_freeze_probe(
                        problem, player_state, total_heuristic, optimal_actions)
                    # TODO: In reverse mode, assign this current_CTG value before calling calculate_at_freeze_probe
                    freeze_probe_data['current_CTG'] = current_CTG
                    # TODO: Change to < if in reverse mode, > for regular mode
                    if current_CTG > cost_to_go[-1]:
                        CTG_increase_count += 1
                    if current_CTG == cost_to_go[-1]:
                        CTG_stays_same += 1
                    cost_to_go.append(current_CTG)
                    freeze_probe_data['mistake_so_far'] = CTG_increase_count
                    freeze_probe_data['redundant_so_far'] = CTG_stays_same
                    freeze_probe_data['next_best_action'] = next_best_action
                else:
                    current_CTG, planner_output, optimal_actions, db_changed = calculate_cost_to_go(problem,
                                                                                                    player_state,
                                                                                                    total_heuristic,
                                                                                                    optimal_actions)
                    # print('Action taken: ', action_label)
                    # TODO: Change to < if in reverse mode
                    if current_CTG > cost_to_go[-1]:
                        CTG_increase_count += 1
                    if current_CTG == cost_to_go[-1]:
                        CTG_stays_same += 1
                    cost_to_go.append(current_CTG)

                if db_changed:
                    save_object(optimal_actions,
                                "problem_config_files/optimal_actions_" + level_name)  # TODO: See why it is taking so long.
        except KeyboardInterrupt:
            save_object(optimal_actions,
                        "problem_config_files/optimal_actions_" + level_name)  # TODO: See why it is taking so long.

        # save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)
        # cost_to_go.pop(0)
        # cost_to_go.reverse()

    plt.plot(cost_to_go)
    plt.scatter(range(len(cost_to_go)), cost_to_go, 5, 'r')
    try:
        plt.axvline(x=freeze_probe_index + 1)
    except TypeError:
        pass
    plt.ylabel('Cost to go')
    plt.xlabel('# Actions')
    plt.grid(color='k', linestyle='-', linewidth=0.25)
    # plt.savefig('problem_config_files/Player_Data/player_CTG_' + filename + '.png')
    # plt.show()
    print('Total Time taken: ', time() - start_time)

    # save_object(optimal_actions, "problem_config_files/optimal_actions_" + level_name)
    return cost_to_go, CTG_increase_count, CTG_stays_same, freeze_probe_data, Q_value_data


if __name__ == '__main__':

    filename = "config_B3_C8_P2_D1_84.json"  # config_B5_C14_P2_D1_20  # "config_B4_C12_P3_D2_69.json"   # "config_B3_C8_P2_D1_84.json"
    print(filename)
    analyze_plan(filename)  # Won't work for now.
