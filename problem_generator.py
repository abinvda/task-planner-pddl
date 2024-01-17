#!/usr/bin/env python

from __future__ import print_function
from operator import itemgetter
import gc
from utils import *

dirname = path.dirname(__file__)

if __name__ == '__main__':
    '''from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)'''

    plan_len_S = []
    platform_S = []
    display_S = []
    redundancy_S = []
    maxPlanLen = 40
    minPlanLen = 32
    for nBox in range(4, 5):
        gc.collect()
        for nExtraComponents in range(8, 9, 2):
            for itr in range(1, 101):
                objects = get_objects(nBox, nExtraComponents)
                boxes_order, compCount, compTarget = randomize_objects(objects, nExtraComponents)
                for nPlatforms in range(3, 4):
                    for nDisplay in range(2, 3):
                        gc.collect()
                        filename = "config_B" + "%d" % nBox + "_C" + "%d" % (
                                nBox + nExtraComponents) + "_P" + "%d" % nPlatforms + "_D" + "%d" % nDisplay + "_" + "%d" % itr
                        print(filename)

                        domain = get_domain(nDisplay)

                        platform_pool = ('I', 'II', 'III', 'IV')  # TODO: Should be a global variable
                        platforms = platform_pool[:nPlatforms]
                        objects['box'] = objects['box'] + platforms
                        init = get_init(objects, compCount, boxes_order, nPlatforms, nDisplay)
                        goal = get_goal(objects, nPlatforms, compTarget)

                        output_stream = {}
                        output_stream['Platforms'] = nPlatforms
                        output_stream['Displays'] = nDisplay
                        output_stream['GridSize'] = {'x': max(objects['gridX']), 'y': max(objects['gridY'])}

                        [problem, output_stream] = get_problem(domain, objects, nPlatforms, output_stream, init, goal, boxes_order, compCount)
                        total_heuristic = get_heuristics(problem, compTarget)

                        # entropy = get_entropy(compTarget, output_stream)

                        # print(entropy)

                        plan, states, states_explored = planner(problem, heuristic=total_heuristic, verbose=True)


                        output_stream['Plan'] = []
                        if plan is None:
                            output_stream['Plan_length'] = 99
                            print('No Plan!')
                        else:
                            #print('initial heuristic', '-->', total_heuristic(states[0]))
                            #for i in range(len(plan)):
                            #    print(plan[i], '-->', total_heuristic(states[i + 1]))
                            #print('\n')

                            for i in range(len(plan)):
                                output_stream['Plan'].append(tuple(plan[i].sig))
                            output_stream['Plan_length'] = len(plan)

                            # Calculate redundancy
                            resource_use = {}
                            if states:
                                resource_use = get_resource_use(states[-1], platforms, objects['station'][0], nDisplay)

                            # Extra info
                            output_stream['ResourceUse'] = resource_use
                            output_stream['StatesExplored'] = states_explored
                            # output_stream['GridEntropy'] = entropy
                            from_planner_to_shared_format(output_stream, "problem_config_files/" + filename + ".json")

                            '''if len(plan) > maxPlanLen:
                                maxPlanLen = len(plan)
                                from_planner_to_shared_format(output_stream, "problem_config_files/" + filename + ".json")

                            if len(plan) < minPlanLen:
                                minPlanLen = len(plan)
                                from_planner_to_shared_format(output_stream,
                                                              "problem_config_files/" + filename + ".json")'''

                            plan_len_S.append([output_stream['Plan_length'], filename])
                            #redundancy_S.append(resource_use['Avg_redundancy'])
                        #break
                    #break
                #break
            #break
            plan_len_S = sorted(plan_len_S, key=itemgetter(0))
            from_planner_to_shared_format(plan_len_S, "problem_config_files/sorted_B" + "%d" % nBox + "_C" + "%d" % (
                                nBox + nExtraComponents) + ".json")
            t = 1



