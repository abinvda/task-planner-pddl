#!/usr/bin/env python

from __future__ import print_function
from multiprocessing import Process, Manager
from utils import *


dirname = path.dirname(__file__)


def read_problem_config(file_name):
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

    # with open(filename, 'w') as output_file:  # Overwrites any existing file.
    #     json_friendly_dict = defaultdict(list)
    #     i = 0
    #     json.dump(objects, output_file, ensure_ascii=False, indent=4)
        # for state in objects:
        #     json_friendly_dict['State%d' % i] = {'Predicates': list(to_json(state, 'pred')), 'Functions': to_json(state, 'func'), 'Actions': to_json(objects[state])}
        #     i += 1
        # json.dump(json_friendly_dict, output_file, ensure_ascii=False, indent=4)
        # output_file.close()


# def to_json(object, type=None):
#     if isinstance(object, State):
#         if type == 'pred':
#             return object.predicates
#         else:
#             return object.functions
#     else:
#         try:
#             action = list()
#             for obj in object:
#                 action.append(obj.sig)
#             return action
#         except AttributeError:
#             print('what class object???')
#             return None
#
#
# def from_json(object, action_list=None):
#     if isinstance(object, dict):
#         return State(object['Predicates'], object['Functions'])
#     else:
#         try:
#             return action_list[object]
#         except KeyError:
#             print('Action not found in grounded action list.')
#             return None


def read_object(filename):
    with open(filename + '.pkl', 'rb') as f:
        return pickle.load(f)


def get_open_list(optimal_path, optimal_actions, problem):
    open_list = set(optimal_path)
    for i in range(4):
        new_states = set()
        for node in open_list:
            successors = set(node.apply(action) for action in problem.grounded_actions if node.is_applicable(action))
            new_states.update(successor for successor in successors if successor not in open_list)  # and successor not in optimal_actions)
        open_list.update(new_states)
        if len(open_list) > 100:
            break
    return open_list


def expand_knowledge(problem, total_heuristic, open_list, optimal_actions):
    optimal_actions = defaultdict(set)
    for k in d.iteritems():
        optimal_actions[pickle.loads(k)] = d[k]
    for node in open_list:
        problem.set_initial_state(node)

        planner_output = planner(problem, heuristic=total_heuristic, verbose=True, nPlans=1,
                                 calculate_all_paths=0, optimal_actions=optimal_actions)

        if planner_output is None:
            print('No Plan!')
        else:
            print('Yes Plan!')
            for plans in planner_output:
                actions, states, states_explored = plans
                # print('initial heuristic', '-->', total_heuristic(states[0]))
                for i in range(len(actions)):
                    if pickle.dumps(states[i]) not in optimal_actions.keys():
                        optimal_actions[pickle.dumps(states[i])].add(actions[i].sig)
                    # print(states[i], '-->  ACTION: ', actions[i])
                    # print(actions[i], '-->', len(actions)-i-1, '-->', total_heuristic(states[i + 1]))
                # print('\n')

if __name__ == '__main__':
    '''from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)'''

    filename = "config_B4_C12_P2_D1_29.json"  # config_B5_C14_P2_D1_20  # "config_B4_C12_P2_D1_46.json"   # "config_B3_C8_P2_D1_84.json"
    print(filename)

    input_stream = read_problem_config("problem_config_files/" + filename)

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

    planner_output = planner(problem, heuristic=total_heuristic, verbose=True, nPlans=1, calculate_all_paths=1, optimal_actions=optimal_actions)

    #plan, states, states_explored = planner(problem, heuristic=total_heuristic, verbose=True)


    if planner_output is None:
        print('No Plan!')
    else:
        output_stream = input_stream
        for plans in planner_output:
            actions, states, states_explored = plans
            # print('initial heuristic', '-->', total_heuristic(states[0]))
            for i in range(len(actions)):
                if states[i] not in optimal_actions.keys():
                    optimal_actions[states[i]].add(actions[i].sig)
                elif actions[i].sig not in optimal_actions[states[i]]:
                    optimal_actions[states[i]].add(actions[i].sig)
                # print(states[i], '-->  ACTION: ', actions[i])
                print(actions[i], '--> CTG:', len(actions)-i-1, '--> H:', total_heuristic(states[i + 1]))
            print('\n')

        save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)

    optimal_path = planner_output[0][1]  # It is the list of states that the optimal path goes through
    open_list = get_open_list(optimal_path, optimal_actions, problem)
    open_list = list(open_list)
    counter = len(open_list)
    try:
        manager = Manager()
        d = manager.dict()
        for k in optimal_actions:
            d[pickle.dumps(k)] = random.sample(optimal_actions[k], 1)[0]
        p1 = Process(target=expand_knowledge, args=(problem, total_heuristic, open_list[:(counter//2)], d))
        p2 = Process(target=expand_knowledge, args=(problem, total_heuristic, open_list[(counter//2):], d))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
            # a = Thread(target=save_object, args=(optimal_actions, "problem_config_files/optimal_actions_" + filename))
            # a.start()
            # a.join()
        save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)
    except KeyboardInterrupt:
        save_object(optimal_actions, "problem_config_files/optimal_actions_" + filename)
    t=1


            # if plans == planner_output[0]:
            #     output_stream['Plan'] = []
            #     for i in range(len(plan)):
            #         output_stream['Plan'].append(tuple(plan[i].sig))
            #     output_stream['Plan_length'] = len(plan)
            #
            #     # Calculate redundancy
            #     resource_use = {}
            #     if states:
            #         platforms = list(set(objects['box']) - set(objects['container']))
            #         # resource_use = get_resource_use(states[-1], platforms, objects['station'][0], nDisplay)
            #
            #     # Extra info
            #     output_stream['ResourceUse'] = resource_use
            #     output_stream['StatesExplored'] = states_explored
            #     # output_stream['GridEntropy'] = entropy
            #     from_planner_to_shared_format(output_stream, "problem_config_files/" + filename)




