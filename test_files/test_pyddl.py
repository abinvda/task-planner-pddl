import unittest
import pyddl
from pyddl import *
import planner
from planner import *

"""
            """


class MyTestCase(unittest.TestCase):

    def setUp(self):

        """
        movebox = Action('movebox',
                         parameters=(('box', 'b1'), ('box', 'b2'),),
                         preconditions=('and', (('movable', 'b1'), ('clear', 'b1'), ('clear', 'b2'),),),
                         effects=(('not', ('clear', 'b2'),),
                                  ('forall', ({'box': 'b'}), ('when', ('top', 'b1', 'b'), (('not', ('top', 'b1', 'b')), ('clear', 'b'),)),),  # assert this
                                  ('top', 'b1', 'b2'),),
                         ),
        movebox_to_station = Action('movebox-to-station',
                                    parameters=(('box', 'b1'), ('station', 's1'),),
                                    preconditions=('and', (('movable', 'b1'), ('clear', 'b1'), ('clear', 's1'),),),
                                    effects=(neg(('clear', 's1')), neg(('clear', 'b1')),('top', 'b1', 's1'),
                                             ('forall', ({'box': 'b'}),('when', ('top', 'b1', 'b'),(('not', ('top', 'b1', 'b')), ('clear', 'b'),)),),
                                             ('forall', ({'component': 'c'}), ('when', ('in', 'c', 'b1'), (('not', ('locked', 'c')),)),)  # assert this ## Just check the number of brackets
                                             ),
                                    ),
        movebox_from_station = Action(
            'movebox-from-station',
            parameters=(
                ('box', 'b1'),
                ('box', 'b2'),
            ),
            preconditions=('and',
                           (
                               ('exists',
                                ({'station': 's'}),
                                ('top', 'b1', 's'),
                                ),
                               ('clear', 'b2'),
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
        ),
        place_component = Action(
            'place-component',
            parameters=(
                ('component', 'c'),
                ('grid', 'x'),
                ('grid', 'y'),
            ),
            preconditions=('and',
                           (
                               ('blank', 'x', 'y'),
                               ('not', ('locked', 'c')),
                           ),
                           ),
            effects=(
                ('at', 'c', 'x', 'y'),
                neg(('unlocked', 'c')),
                neg(('blank', 'x', 'y')),
            ),
        ),
        """

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

        self.domain_main = Domain((
            movebox, move_to_station, move_from_station, place_component,

        ))
        self.objects = {
            'box': ('box_cir', 'box_tri', 'box_rec', 'I', 'II', 'III'),
            'station': ('stat1',),
            'component': ('circle', 'triangle', 'rectangle'),
            'grid': (1, 2, 3),
        }

        self.problem1 = Problem(
            self.domain_main,
            self.objects,
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
                ('top', 'box_cir', 'II'),
                ('clear', 'box_tri'),
                (('not', ('locked', 'circle'),),),

            ),
            precedence={}
        )

    def NOtest_actionGrounding(self):
        for actions in self.problem1.grounded_actions:
            print(actions, "   , preconds: ", actions.grounded_preconditions)
            # print(actions)  # , "    ", actions.grounded_effects)

        self.assertEqual(True, True)

    def test_applicability(self):
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
        for action in self.problem1.grounded_actions:
            if self.state1.is_applicable(action.grounded_preconditions):
                new_state = self.state1.apply(action)
                print(action, "   , new_state:  ", new_state.predicates)
        self.assertEqual(1, 1)

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






if __name__ == '__main__':
    unittest.main()
