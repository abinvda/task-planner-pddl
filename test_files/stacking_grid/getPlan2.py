#!/usr/bin/env python

from __future__ import print_function
from pyddl import Domain, Problem, Action, neg
from planner import *
import math
from get_domain2 import *


objects = {
    'box': ('box_cir', 'box_tri', 'box_sqr', 'I', 'II', 'III'),
    'container': ('box_cir', 'box_tri', 'box_sqr'),
    'station': ('stat1',),
    'component': ('circle', 'triangle', 'square', 'base_x1', 'base_x2', 'base_x3'),
    'component_only': ('circle', 'triangle', 'square'),
    'gridX': ('x1', 'x2', 'x3'),
    'gridY': (1, 2, 3),
}


def problem(verbose):
    domain = get_domain2(3, gridHeight=3)

    problem = Problem(
        domain,
        objects,
        static_literals=(
            ('movable', 'box_cir'),
            ('movable', 'box_sqr'),
            ('movable', 'box_tri'),

            ('movable', 'triangle'),
            ('movable', 'circle'),
            ('movable', 'square'),

            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'square', 'box_sqr'),

        ),
        init=(
            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'square', 'box_sqr'),

            #('at', 'circle', 0, 0),
            #('at', 'triangle', 0, 0),
            #('at', 'rectangle', 0, 0),

            ('=', ('count', 'circle'), 3),  # ('=', ('count', 'circle', 'box_cir'), 1),
            ('=', ('count', 'triangle'), 3),
            ('=', ('count', 'square'), 2),

            ('=', ('visible', 'circle'), 0),
            ('=', ('visible', 'triangle'), 0),
            ('=', ('visible', 'square'), 0),

            ('=', ('onGrid', 'circle'), 0),
            ('=', ('onGrid', 'triangle'), 0),
            ('=', ('onGrid', 'square'), 0),

            ('=', 'displayMax', 3),
            ('=', 'displayCurr', 0),

            ('=', ('height', 'x1'), 0),
            ('=', ('height', 'x2'), 0),
            ('=', ('height', 'x3'), 0),

            ('top', 'box_tri', 'box_sqr'),
            ('top', 'box_sqr', 'box_cir'),
            ('top', 'box_cir', 'I'),
            ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('clear', 'base_x1'),
            ('clear', 'base_x2'),
            ('clear', 'base_x3'),

            ('belongs', 'base_x1', 'x1'),
            ('belongs', 'base_x2', 'x2'),
            ('belongs', 'base_x3', 'x3'),

            ('top', 'square', 'nothing'),
            ('top', 'triangle', 'nothing'),
            ('top', 'circle', 'nothing'),

            #('blank', 1, 1),  # grid at (1,1) is blank
            #('blank', 1, 2),
            #('blank', 2, 1),
            #('blank', 2, 2),
            #('blank', 2, 3),

        ),
        goal=(
            # ('top', 'box_tri', 'box_sqr'),
            # ('top', 'box_sqr', 'box_cir'),
            # ('top', 'box_cir', 'I'),
            # ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('top', 'square', 'triangle'),
            ('top', 'triangle', 'circle'),
            ('top', 'circle', 'base_x1'),

            ('top', 'circle', 'square'),
            ('top', 'square', 'circle'),
            ('top', 'circle', 'base_x2'),

            ('top', 'triangle', 'triangle'),
            ('top', 'triangle', 'base_x3'),
        ),
        # Reminder: the tuples should end with a comma for multiple conditions and not for a single one. TODO: FIX THIS.
        precedence={}
    )

    def box_position(state):
        boxDict = {}
        for pq in state:
            if pq[0] == 'top':
                boxDict[pq[1]] = (pq[2])
        return boxDict

    goal_boxDict = box_position(problem.goals)

    def box_mismatch_heuristic(state):
        state_boxDict = box_position(state.predicates)
        dist = 0
        # print(state_boxDict)
        for k in goal_boxDict.keys():
            # print(state_boxDict[k])
            # print(goal_boxDict[k])
            b1 = goal_boxDict[k]
            try:
                b2 = state_boxDict[k]
                if b1 != b2:
                    dist += 1
            except:
                pass

        return dist

    def total_heuristic(state):
        dist = 1*componentCost(state) + 1*box_mismatch_heuristic(state)
        #dist = 1 * box_mismatch_heuristic(state)
        return dist

    def componentCost(state):
        dist = 0

        temp_dict = {}
        for box, component in zip(problem.objects['container'], problem.objects['component_only']):
            temp_dict[component] = box

        for comp in problem.objects['component_only']:
            box_needed = 0
            component_reqd = state.f_dict[('count', comp)]  # No. of components required to unlock
            if component_reqd > 0:  # If component is not unlocked
                #dist += component_reqd
                box_needed = 1

            if box_needed:  # If the box(container) is required to unlock a component
                box = temp_dict[comp]
                if ('top', box, 'stat1') not in state.predicates:
                    dist += 1
                    # if ('clear', 'stat1') not in state.predicates:
                    #   dist += 1
                    for other_box in objects['container']:
                        if ('top', other_box, box) in state.predicates:
                            dist += 1
                            for yet_another_box in objects['container']:
                                if ('top', yet_another_box, other_box) in state.predicates:
                                    dist += 1
                                    for yet_yet_another_box in objects['container']:
                                        if ('top', yet_yet_another_box, yet_another_box) in state.predicates:
                                            dist += 1
                                            # for yet_yet_yet_another_box in objects['box']:
                                            #   if ('top', yet_yet_yet_another_box, yet_yet_another_box) in state.predicates:
                                            #      dist += 1
                                            break
                                    break
                            break

        return dist

    planner_output = planner(problem, heuristic=total_heuristic, verbose=verbose)
    plan, states, states_explored = planner_output[0]
    if plan is None:
        print('No Plan!')
    else:
        print('initial heuristic', '-->', total_heuristic(states[0]))
        for i in range(len(plan)):
            print(plan[i], '-->', total_heuristic(states[i+1]))
        #for action in plan:
         #   print(action)
        #for state in states:
            #print(state)
         #   print(total_heuristic(state))



if __name__ == '__main__':
    '''from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)'''
    problem(True)
