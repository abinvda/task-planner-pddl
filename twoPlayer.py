#!/usr/bin/env python

from __future__ import print_function
from pyddl import Domain, Problem, Action, neg
from planner import *
import time
import math
import cursesmenu
from cursesmenu import SelectionMenu
from pick import pick


# Actions
movebox = Action(
    'movebox',
    parameters=(
        ('box', 'b1'),
        ('box', 'b2'),
    ),
    static_preconditions=(('movable', 'b1'),
                          ),
    preconditions=('and',
                   (
                       ('clear', 'b1'),
                       ('clear', 'b2'),

                   ),
                   ),
    effects=(
        ('not',
         ('clear', 'b2'),
         ),
        ('forall',
         ({'box': 'b'}),  # , 'component': 'c'}),  # for all box b
         ('when',
          ('top', 'b1', 'b'),
          (('not', ('top', 'b1', 'b')), ('clear', 'b'),)  # assert this
          ),
         ),
        ('top', 'b1', 'b2'),
    ),
)

move_to_station = Action(
    'move_to_station',
    parameters=(
        ('box', 'b1'),
        ('station', 's1'),
    ),
    static_preconditions=(('movable', 'b1'),
                          ),
    preconditions=('and',
                   (
                       ('clear', 'b1'),
                       ('clear', 's1'),
                       ('<', 'displayCurr', 3),
                   ),
                   ),
    effects=(
        neg(('clear', 's1')),
        neg(('clear', 'b1')),
        ('top', 'b1', 's1'),
        ('forall',
         ({'box': 'b'}),
         ('when',
          ('top', 'b1', 'b'),
          (('not', ('top', 'b1', 'b')), ('clear', 'b'),)  # assert this
          ),
         ),
        ('forall',
         ({'component': 'c'}),
         ('when',
          ('in', 'c', 'b1'),  # and ('<=', 'displayCurr', 3),
          (('+=', ('visible', 'c'), 1),
           ('-=', ('count', 'c'), 1),
           ('+=', 'displayCurr', 1),
           )  # When error, check the number of brackets
          ),
         )
    ),
)

move_from_station = Action(
    'move_from_station',
    parameters=(
        ('box', 'b1'),
        ('box', 'b2'),
    ),
    static_preconditions=(('movable', 'b1'),
                          ),
    preconditions=('and',
                   (
                       ('clear', 'b2'),
                       # ('top', 'b1', 'stat1'),
                       ('exists',
                        ({'station': 's'}),
                        ('top', 'b1', 's'),
                        ),
                   ),
                   ),
    effects=(
        neg(('clear', 'b2')),
        ('top', 'b1', 'b2'),
        ('clear', 'b1'),
        ('forall',
         ({'station': 's'}),
         ('when',
          ('top', 'b1', 's'),
          (('not', ('top', 'b1', 's')), ('clear', 's'),)  # assert this
          ),
         ),
    ),
)

place_component = Action(
    'place_component',
    parameters=(
        ('component', 'c'),
        ('grid', 'X'),
        ('grid', 'Y'),
    ),
    static_preconditions=(),
    preconditions=('and',
                   (
                       ('blank', 'X', 'Y'),
                       ('>', ('visible', 'c'), 0),
                       # ('forall',
                       # ({'component': 'c1'}),
                       # ('when',
                       # ('!=', 'c', 'c1'),
                       # ('locked', 'c1')  # assert this
                       # ),
                       # ),
                   ),
                   ),
    effects=(
        ('at', 'c', 'X', 'Y'),
        neg(('blank', 'X', 'Y')),
        neg(('at', 'c', 0, 0)),
        ('-=', 'displayCurr', 1),
        ('-=', ('visible', 'c'), 1),
    ),
    unique=False,
)

return_component = Action(
    'return_component',
    parameters=(
        ('component', 'c'),
        ('box', 'b1'),
    ),
    static_preconditions=(('movable', 'b1'),
                          ('in', 'c', 'b1'),
                          ),
    preconditions=('and',
                   (
                       ('exists',
                        ({'station': 's'}),
                        ('top', 'b1', 's'),
                        ),
                       ('>', ('visible', 'c'), 0),
                   ),
                   ),
    effects=(
        ('locked', 'c'),
        ('-=', 'displayCurr', 1),
        ('+=', ('count', 'c'), 1),
        ('-=', ('visible', 'c'), 1),
        # component count += 1,
    ),
    unique=True,
)

objects = {
    'box': ('box_cir', 'box_tri', 'box_rec', 'I', 'II', 'III'),
    'station': ('stat1',),
    'component': ('circle', 'triangle', 'rectangle'),
    'grid': (1, 2, 3),
}


def problem(verbose):
    domain = Domain((
        movebox, move_to_station, move_from_station, place_component,
    ))
    problem = Problem(
        domain,
        objects,
        static_literals=(
            ('movable', 'box_cir'),
            ('movable', 'box_rec'),
            ('movable', 'box_tri'),
        ),
        init=(
            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'rectangle', 'box_rec'),

            ('at', 'circle', 0, 0),
            ('at', 'triangle', 0, 0),
            ('at', 'rectangle', 0, 0),

            ('=', ('count', 'circle'), 1),  # ('=', ('count', 'circle', 'box_cir'), 1),
            ('=', ('count', 'triangle'), 1),
            ('=', ('count', 'rectangle'), 2),

            ('=', ('visible', 'circle'), 0),
            ('=', ('visible', 'triangle'), 0),
            ('=', ('visible', 'rectangle'), 0),

            ('=', 'displayMax', 3),
            ('=', 'displayCurr', 0),

            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'box_cir'),
            ('top', 'box_cir', 'I'),
            ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('blank', 1, 1),  # grid at (1,1) is blank
            ('blank', 1, 2),
            ('blank', 2, 1),
            ('blank', 2, 2),
            ('blank', 2, 3),
        ),
        goal=(
            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'box_cir'),
            ('top', 'box_cir', 'I'),
            ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('at', 'circle', 1, 1),
            ('at', 'triangle', 1, 2),
            ('at', 'rectangle', 2, 1),
            ('at', 'rectangle', 2, 2),
        ),
        # Reminder: the tuples should end with a comma for multiple conditions and not for a single one. TODO: FIX THIS.
        precedence={('place_component', 'triangle', 1, 2): (('at', 'rectangle', 2, 1),),
                    ('place_component', 'circle', 1, 1): (('at', 'rectangle', 2, 1),),
                    ('place_component', 'rectangle', 2, 1): (('at', 'rectangle', 2, 2),)}  # ,
        )

    plan, states = planner(problem, heuristic=total_heuristic, verbose=verbose)
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

def get_heuristics(problem):

    def box_position(state):
        boxDict = {}
        for pq in state:
            if pq[0] == 'top':
                boxDict[pq[1]] = (pq[2])
        return boxDict

    def predicate_match(predicates):
        result = {'neg': [], 'pos': []}
        for pred in predicates:
            if pred[0] == 'not':
                result['neg'].append(pred[1])
            else:
                result['pos'].append(pred)
        return result

    def predicate_match_heuristic(state):
        h = 0
        sub_goal_conds = predicate_match(problem.goals)
        for lits in state.predicates:
            if lits not in sub_goal_conds['pos']:
                h = h + 1
            if lits in sub_goal_conds['neg']:
                pass  # h = h + 1
        return h

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
        dist = 1 * componentCost(state) + 1 * box_mismatch_heuristic(state)
        # dist = 1 * distance_heuristic(state) + 1 * box_mismatch_heuristic(state)
        return dist

    def componentCost(state):
        dist = 0

        for p in state.predicates:
            if p[0] == 'in':  # if the predicate is (in, component, box)
                for p2 in state.predicates:
                    if p2[0] == 'at' and p2[1] == p[
                        1]:  # if the predicate is (at, component, x, y) and it's the same component from outer loop
                        if p2 in problem.goals:
                            break
                        else:
                            dist += 1
                            for p3 in state.f_dict:
                                if p3[0] == 'visible' and p3[1] == p[1] and state.f_dict[
                                    p3] < 1:  # if the component is not on display
                                    dist += 1
                                    for p4 in state.predicates:
                                        if p4[0] == 'top' and p4[2] == p[
                                            2]:  # if the predicate is (top, something2, something1)
                                            dist += 1
                                            for p5 in state.predicates:
                                                if p5[0] == 'top' and p5[2] == p4[
                                                    1]:  # if the predicate is (top, something2, something1)
                                                    dist += 1
                                                    break
                                            break
                                    break
                        break

        return dist

    return total_heuristic

def get_next_best_action(problem, state, heuristics):
    problem.set_initial_state(state)
    plan, states = planner(problem, heuristic=heuristics, verbose=False)
    if len(plan) == 0:
        print('No Plan!')
        return None
    else:
        return plan[0]

def get_sub_best_action(problem, state, heuristics):
    problem.set_initial_state(state)
    plan, states = sub_optimal_planner(problem, heuristic=heuristics, verbose=False)
    if len(plan) == 0:
        print('No Plan!')
        return None
    else:
        return plan[0]

def startGame():
    domain = Domain((
        movebox, move_to_station, move_from_station, place_component,))

    problem = Problem(
        domain,
        objects,
        static_literals=(
            ('movable', 'box_cir'),
            ('movable', 'box_rec'),
            ('movable', 'box_tri'),
        ),
        init=(
            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'rectangle', 'box_rec'),

            ('at', 'circle', 0, 0),
            ('at', 'triangle', 0, 0),
            ('at', 'rectangle', 0, 0),

            ('=', ('count', 'circle'), 1),  # ('=', ('count', 'circle', 'box_cir'), 1),
            ('=', ('count', 'triangle'), 1),
            ('=', ('count', 'rectangle'), 2),

            ('=', ('visible', 'circle'), 0),
            ('=', ('visible', 'triangle'), 0),
            ('=', ('visible', 'rectangle'), 0),

            ('=', 'displayMax', 3),
            ('=', 'displayCurr', 0),

            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'box_cir'),
            ('top', 'box_cir', 'I'),
            ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('blank', 1, 1),  # grid at (1,1) is blank
            ('blank', 1, 2),
            ('blank', 2, 1),
            ('blank', 2, 2),
            ('blank', 2, 3),
        ),
        goal=(
            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'box_cir'),
            ('top', 'box_cir', 'I'),
            ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('at', 'circle', 1, 1),
            ('at', 'triangle', 1, 2),
            ('at', 'rectangle', 2, 1),
            ('at', 'rectangle', 2, 2),
        ),
        # Reminder: the tuples should end with a comma for multiple conditions and not for a single one. TODO: FIX THIS.
        precedence={('place_component', 'triangle', 1, 2): (('at', 'rectangle', 2, 1),),
                    ('place_component', 'circle', 1, 1): (('at', 'rectangle', 2, 1),),
                    ('place_component', 'rectangle', 2, 1): (('at', 'rectangle', 2, 2),)}  # ,
    )
    state = problem.initial_state
    heuristics = get_heuristics(problem)

    i = 1

    while i < 15:
        planner_action = get_next_best_action(problem, state, heuristics)
        if planner_action is None:
            print('You have failed this city..')
            break
        else:
            print('Opt:  ', planner_action)
        state = state.apply(planner_action)

        a_list = problem.grounded_actions
        title = 'Please select next action: '

        # Display actions options to select
        # option, action_index = pick(a_list, title)
        # action_index = SelectionMenu.get_selection(a_list)
        # user_action = a_list[action_index]

        #if next_state.is_applicable(user_action.sorted_preconditions):
        #    next_state = next_state.apply(planner_action)
        #else:
        #    print('Invalid action, go again.')
        #    continue

        sub_planner_action = get_sub_best_action(problem, state, heuristics)
        if sub_planner_action is None:
            print('You have failed this city..')
            break
        else:
            print('Sub:  ', sub_planner_action)
        state = state.apply(sub_planner_action)

        i = i+1



if __name__ == '__main__':
    '''from optparse import OptionParser
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option('-q', '--quiet',
                      action='store_false', dest='verbose', default=True,
                      help="don't print statistics to stdout")

    # Parse arguments
    opts, args = parser.parse_args()
    problem(opts.verbose)'''
    startGame()
