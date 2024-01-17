from __future__ import print_function
from pyddl import *
import planner
from planner import *
from get_domain import get_domain
from get_precedence import *
from solve_from_shared_format import get_heuristic


def setUp():

    domain_main = get_domain(1)

    objects = {
        'box': ('box_cir', 'box_tri', 'box_rec', 'I', 'II', 'III'),
        'station': ('stat1',),
        'component': ('circle', 'triangle', 'rectangle'),
        'gridX': (1, 2, 3),
        'gridY': (1, 2, 3),
    }

    problem = Problem(
        domain_main,
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

            ('at', 'circle', 2, 1),
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
            #('blank', 2, 1),
            ('blank', 2, 2),
            ('blank', 2, 3),

            ),
        goal=(
            #('top', 'box_tri', 'box_rec'),
            #('top', 'box_rec', 'box_cir'),
            #('top', 'box_cir', 'II'),
            #('clear', 'box_tri'),
            #(('not', ('locked', 'circle'),),),
            ('at', 'circle', 1, 1),
            ('at', 'triangle', 1, 2),

        ),
        precedence=get_precedence()
    )
    return problem

'''def NOtest_actionGrounding(self):
    for actions in self.problem1.grounded_actions:
        print(actions, "   , preconds: ", actions.grounded_preconditions)
        # print(actions)  # , "    ", actions.grounded_effects)

    self.assertEqual(True, True)

def NOtest_applicability(self):
    # test if a grounded action is applicable in a given state

    init2 = (
               ('in', 'circle', 'box_cir'),
               ('in', 'triangle', 'box_tri'),
               ('in', 'rectangle', 'box_rec'),

               ('at', 'circle', 0, 0),
               ('at', 'triangle', 0, 0),
               ('at', 'rectangle', 0, 0),

               ('=', ('count', 'circle'), 1),  # ('=', ('count', 'circle', 'box_cir'), 1),
               ('=', ('count', 'triangle'), 1),
               ('=', ('count', 'rectangle'), 2),

               ('=', ('visible', 'circle'), 1),
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
    predicates = list()
    functions = dict()
    for predicate in init2[0]:
        if predicate[0] == '=':
            functions[predicate[1]] = predicate[2]
        else:
            predicates.append(predicate)
    self.initial_state = State(predicates, functions)

    self.state1 = pyddl.State(predicates, functions, cost=0, predecessor=None)

    for action in self.problem1.grounded_actions:
        if action.name == 'move_from_station':
            result = self.state1.is_applicable(action.sorted_preconditions)
            print(action, "   , result:  ", result)

    self.assertEqual(1, 1)

def NOtest_apply(self):
    predicates = (
                     ('top', 'box_tri', 'box_rec'),
                     ('top', 'box_rec', 'I'),
                     ('top', 'box_cir', 'II'),
                     ('clear', 'box_tri'),
                     ('clear', 'box_cir'),
                     ('clear', 'III'),
                     ('clear', 's'),
                 ),
    self.state1 = pyddl.State(predicates, functions=dict(), cost=0, predecessor=None)
    for action in self.problem.grounded_actions:
        if self.state1.is_applicable(action.grounded_preconditions):
            new_state = self.state1.apply(action)
            print(action, "   , new_state:  ", new_state.predicates)
    #self.assertEqual(1, 1)
    
    def NOtest_simple_task(self):
    problem2 = Problem(
        self.domain1,
        {
            'box': ('box_cir', 'box_tri', 'box_rec'),
            'platform': ('I', 'II', 'III'),
            'station': ('s'),
            'component': ('circle'),
        },
        init=(
            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'box_cir'),
            ('top', 'box_cir', 'I'),
            ('clear', 'box_tri'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('clear', 's'),
            ('locked', 'circle'),
            ('in', 'circle', 'box_cir'),
        ),
        goal=(
            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'I'),
            ('clear', 'box_tri'),
            ('on', 'box_cir', 's'),
            ('clear', 'II'),
            ('clear', 'III'),
            ('not', ('locked', 'circle'),),
        ),
        precedence={}
    )

    plan = planner(problem2)
    if plan is None:
        print('No Plan!')
    else:
        for action in plan:
            print(action)

    self.assertEqual(1, 1)

def NOtest_move_from_station(self):
    problem = Problem(
        domain_main,
        {
            'box': ('box_cir', 'box_tri', 'box_rec', 'I', 'II', 'III'),
            'station': ('stat1',),
            'component': ('circle', 'triangle', 'rectangle-1', 'rectangle-2'),
            'grid': (1, 2),
        },
        init=(
            ('movable', 'box_cir'),
            ('movable', 'box_rec'),
            ('movable', 'box_tri'),

            ('in', 'circle', 'box_cir'),
            ('in', 'triangle', 'box_tri'),
            ('in', 'rectangle-1', 'box_rec'),
            ('in', 'rectangle-2', 'box_rec'),

            ('at', 'circle', 0, 0),
            ('at', 'triangle', 0, 0),
            ('at', 'rectangle-1', 0, 0),
            ('at', 'rectangle-2', 0, 0),

            ('locked', 'circle'),
            ('locked', 'triangle'),
            ('locked', 'rectangle-1'),
            ('locked', 'rectangle-2'),

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
        ),
        goal=(
            ('top', 'box_tri', 'box_rec'),
            ('top', 'box_rec', 'box_cir'),
            ('top', 'box_cir', 'II'),
            ('clear', 'box_tri'),

            ('clear', 'I'),
            ('clear', 'III'),
            ('clear', 'stat1'),

            ('at', 'circle', 1, 1),
            ('at', 'triangle', 1, 2),
            ('at', 'rectangle-1', 2, 1),
            ('at', 'rectangle-2', 2, 2),
        ),
        precedence={('place-component', 'triangle', 1, 2): ('at', 'rectangle-1', 2, 1),
                    ('place-component', 'circle', 1, 1): ('at', 'rectangle-1', 2, 1),
                    ('place-component', 'rectangle-1', 2, 1): ('at', 'rectangle-2', 2, 2)}  # '
        )


'''


def test_plan(problem):

    plan, states, states_explored = planner(problem, verbose=True)
    if plan is None:
        print('No Plan!')
    else:
        #print('initial heuristic', '-->', total_heuristic(states[0]))
        for i in range(len(plan)):
            print(plan[i])  # , '-->', total_heuristic(states[i + 1]))
        print('\n')

def test_apply():
    predicates = {('at', 'circle', 1, 1),  # grid at (1,1) is blank
            ('blank', 1, 2),
            ('blank', 2, 1),
            ('blank', 2, 2),
            ('blank', 2, 3),

            }


    state1 = pyddl.State(predicates, functions=dict(), cost=0, predecessor=None)
    for action in problem.grounded_actions:
        if action.name == 'grid_to_grid':
            t = 1
        if state1.is_applicable(action):
            new_state = state1.apply(action)
            print(action, "   , new_state:  ", new_state.predicates)

if __name__ == '__main__':
    problem = setUp()
    #total_heuristic = get_heuristic(problem, compTarget2)

    #test_apply()
    test_plan(problem)