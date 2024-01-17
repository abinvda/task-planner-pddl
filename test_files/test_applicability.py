import pyddl
from pyddl import *

# test if a grounded action is applicable in a given state


domain1 = Domain((
    Action(
        'movebox',
        parameters=(
            ('box', 'b1'),
            ('box', 'b2'),
        ),
        preconditions=('and',
                       (
                           ('clear', 'b1'),
                           ('exists',
                            ({'box': 'b'}),
                            ('clear', 'b'),
                            ),
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
              ('clear', 'b'),  # assert this
              ),
             ),
            ('forall',
             ({'platform': 'p'}),  # , 'component': 'c'}),  # for all box b
             ('when',
              ('top', 'b1', 'p'),
              ('clear', 'p'),  # assert this
              ),
             ),
            ('top', 'b1', 'b2'),
        ),
    ),

))

problem1 = Problem(
    domain1,
    {
        'box': ('box_cir', 'box_tri', 'box_rec'),
        'platform': ('I', 'II', 'III'),
        'station': ('s'),
        'component': ('circle', 'triangle', 'rectangle'),
        'grid': (1, 2),
    },
    init=(
        ('top', 'box_tri', 'box_rec'),
        ('top', 'box_rec', 'box_cir'),
        ('top', 'box_cir', 'I'),
        ('clear', 'box_tri'),
        ('clear', 'II'),
        ('clear', 'III'),
        ('clear', 's'),
    ),
    goal=(
        ('top', 'box_tri', 'box_rec'),
        ('top', 'box_rec', 'box_cir'),
        ('top', 'box_cir', 'II'),
        ('clear', 'box_tri'),
    ),
    precedence={}
)

for actions in problem1.grounded_actions:
    print(actions, "    , preconds: ", actions.grounded_preconditions)
    # print(actions)  # , "    ", actions.grounded_effects)

predicates = (
                 ('top', 'box_tri', 'box_rec'),
                 ('top', 'box_rec', 'box_cir'),
                 ('top', 'box_cir', 'I'),
                 ('clear', 'box_tri'),
                 ('clear', 'II'),
                 ('clear', 'III'),
                 ('clear', 's'),
             ),
state1 = pyddl.State(predicates, functions=dict(), cost=0, predecessor=None)

for action in problem1.grounded_actions:
    result = state1.is_applicable(action.grounded_preconditions)
    print(action, "   , result:  ", result)