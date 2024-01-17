#!/usr/bin/env python

from __future__ import print_function
from pyddl import Domain, Problem, Action, neg
from planner import *
from utils import *
import math


objects = {
    'box': ('box_cir', 'box_tri', 'box_sqr', 'I', 'II', 'III'),
    'container0000': ('box_cir', 'box_tri', 'box_sqr'),
    'station': ('stat1',),
    'component': ['circle', 'triangle', 'square'],
    'gridX': [1, 2, 3],
    'gridY': [1, 2, 3],
}


def problem(verbose):
    domain = get_domain(1)
    problem = Problem(
        domain,
        objects,
        static_literals=(
            ('movable', 'box_cir'),
            ('movable', 'box_sqr'),
            ('movable', 'box_tri'),
            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'square', 'box_sqr'),

        ),
        init=(
            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'rectangle', 'box_rec'),

            ('=', ('count', 'circle'), 3),  # ('=', ('count', 'circle', 'box_cir'), 1),
            ('=', ('count', 'triangle'), 3),
            ('=', ('count', 'square'), 2),

            ('=', ('visible', 'circle'), 0),
            ('=', ('visible', 'triangle'), 0),
            ('=', ('visible', 'square'), 0),

            ('=', ('onGrid', 'circle'), 0),
            ('=', ('onGrid', 'triangle'), 0),
            ('=', ('onGrid', 'square'), 0),

            ('=', 'displayMax', 1),
            ('=', 'displayCurr', 0),

            ('top', 'box_cir', 'box_sqr'),
            ('top', 'box_sqr', 'box_tri'),
            ('top', 'box_tri', 'I'),
            ('clear', 'box_cir'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('blank', 1, 1),  # grid at (1,1) is blank
            ('blank', 1, 2),
            ('blank', 1, 3),
            ('blank', 2, 1),
            ('blank', 2, 2),
            ('blank', 2, 3),
            ('blank', 3, 1),
            ('blank', 3, 2),
            ('blank', 3, 3),

        ),
        goal=(
            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'rectangle', 'box_rec'),

            ('=', ('count', 'circle'), 1),  # ('=', ('count', 'circle', 'box_cir'), 1),
            ('=', ('count', 'triangle'), 2),
            ('=', ('count', 'square'), 0),

            ('=', ('visible', 'circle'), 0),
            ('=', ('visible', 'triangle'), 0),
            ('=', ('visible', 'square'), 0),

            ('=', ('onGrid', 'circle'), 2),
            ('=', ('onGrid', 'triangle'), 1),
            ('=', ('onGrid', 'square'), 2),

            ('=', 'displayMax', 1),
            ('=', 'displayCurr', 0),

            ('top', 'box_cir', 'box_sqr'),
            ('top', 'box_sqr', 'box_tri'),
            ('top', 'box_tri', 'II'),  # I -> II
            ('clear', 'box_cir'),
            ('clear', 'I'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            # ('blank', 1, 1),  # grid at (1,1) is blank
            # ('blank', 1, 2),
            # ('blank', 1, 3),
            # ('blank', 2, 1),
            # ('blank', 2, 2),
            ('blank', 2, 3),
            ('blank', 3, 1),
            ('blank', 3, 2),
            ('blank', 3, 3),

            # ('clear', 'II'),
            # ('clear', 'stat1'),

            ('at', 'circle', 1, 1),
            ('at', 'circle', 1, 3),
            ('at', 'triangle', 1, 2),
            ('at', 'square', 2, 1),
            ('at', 'square', 2, 2),
        ),
        # Reminder: the tuples should end with a comma for multiple conditions and not for a single one
        precedence=get_precedence()
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
            b2 = state_boxDict[k]
            if b1 != b2:
                dist += 1
        return dist

    def total_heuristic(state):
        dist = 1*box_mismatch_heuristic(state) + 1*componentCost(state)
        #dist = 1 * distance_heuristic(state) + 1 * box_mismatch_heuristic(state)
        return dist

    def componentCost(state):
        dist = 0
        for p in state.predicates:
            if p[0] == 'in':  # if the predicate is (in, component, box)
                for p2 in state.predicates:
                    if p2[0] == 'at' and p2[1] == p[1]: # if the predicate is (at, component, x, y) and it's the same component from outer loop
                        if p2 in problem.goals:
                            break
                        else:
                            dist += 1
                            for p3 in state.f_dict:
                                if p3[0] == 'visible' and p3[1] == p[1] and state.f_dict[p3] < 1:  # if the component is not on display
                                    dist += 1
                                    for p4 in state.predicates:
                                        if p4[0] == 'top' and p4[2] == p[2]:  # if the predicate is (top, something2, something1)
                                            dist += 1
                                            for p5 in state.predicates:
                                                if p5[0] == 'top' and p5[2] == p4[1]:  # if the predicate is (top, something2, something1)
                                                    dist += 1
                                                    break
                                            break
                                    break
                        break

        return dist

    '''
    def componentCostOld(state):
        dist = 0

        for p in state.predicates:
            if p[0] == 'in':  # if the predicate is (in, component, box)
                for p2 in state.predicates:
                    if p2[0] == 'at' and p2[1] == p[1]: # if the predicate is (at, component, x, y) and it's the same component from outer loop
                        if p2 in problem.goals:
                            break
                        else:
                            dist += 1
                            for p3 in state.predicates:
                                if p3[0] == 'top' and p3[1] == p[2] and p3[2] != 'stat1':  # if the predicate is (top, box, something) and 'something' is not the station
                                    dist += 1
                                if p3[0] == 'top' and p3[2] == p[2]:  # if the predicate is (top, something1, box)
                                    dist += 1
                                    for p4 in state.predicates:
                                        if p4[0] == 'top' and p4[2] == p3[1]:  # if the predicate is (top, something2, something1)
                                            dist += 1


        # a = [pr for pr in state.predicates if pr[0] == 'in']

        return dist
        '''

    planner_output1 = planner(problem, heuristic=total_heuristic, verbose=verbose)
    planner_output2 = bidirectional_planner(problem, heuristic=None)  # [total_heuristic, total_heuristic])
    if planner_output1 is None:
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
