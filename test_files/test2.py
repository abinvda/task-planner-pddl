import pyddl
from pyddl import *

action1 = Action('movebox',
                 parameters=(
                     ('box', 'b1'),
                     ('box', 'b2'),
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
                       ('clear', 'b'),  # assert this
                       ),
                      ),
                     ('top', 'b1', 'b2'),
                 ),
                 )
"""
print(action1)
precedence = {}
grAction1 = _GroundedAction(action1, precedence, ('box_cir', 'box_tri'))
print(grAction1)
"""
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
              ('clear', 'b'),  # assert this
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
    print(actions, "    ", actions.conditional_effects)
