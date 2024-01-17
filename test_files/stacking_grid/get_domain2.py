from pyddl import Domain, Problem, Action, neg


def get_domain2(displayMax, gridHeight = 4):
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

    unlock_component = Action(
        'unlock_component',
        parameters=(
            ('box', 'b1'),
            ('component', 'c'),
        ),
        static_preconditions=(('movable', 'b1'), ('in', 'c', 'b1'),
                              ),
        preconditions=('and',
                       (
                           ('<', 'displayCurr', displayMax),  # TODO: make domain free from parameters (displayMax)
                           ('exists',
                            ({'station': 's'}),
                            ('top', 'b1', 's'),
                            ),
                           ('>', ('count', 'c'), 0),

                       ),
                       ),
        effects=(
            ('+=', ('visible', 'c'), 1),
            ('-=', ('count', 'c'), 1),
            ('+=', 'displayCurr', 1),
        ),

        unique=False,
    )

    place_component = Action(  #### NOW GridX is also a component
        'place_component',
        parameters=(
            ('component', 'c1'),
            ('component', 'c2'),
        ),
        static_preconditions=(('movable', 'c1'),
                              ),
        preconditions=('and',
                       (
                           ('clear', 'c2'),
                           ('>', ('visible', 'c1'), 0),
                           ('forall',
                            ({'gridX': 'x'}),
                            ('when',
                             ('belongs', 'c2', 'x'),
                             (('<', ('height', 'x'), gridHeight))
                             ),
                            ),

                       ),
                       ),
        effects=(
            neg(('clear', 'c2')),
            ('clear', 'c1'),
            ('top', 'c1', 'c2'),
            neg(('top', 'c1', 'nothing')),
            ('forall',
             ({'gridX': 'x'}),
             ('when',
              ('belongs', 'c2', 'x'),
              (('belongs', 'c1', 'x'), ('+=', ('height', 'x'), 1))
              ),
             ),

            ('-=', 'displayCurr', 1),
            ('-=', ('visible', 'c1'), 1),
            ('+=', ('onGrid', 'c1'), 1),

        ),
        unique=False,
    )

    unplace_component = Action(  #### NOW GridX is also a component
        'unplace_component',
        parameters=(
            ('component', 'c1'),
           ),
        static_preconditions=(('movable', 'c1'),
                              ),
        preconditions=('and',
                       (
                           ('clear', 'c1'),
                           ('<', 'displayCurr', displayMax),

                       ),
                       ),
        effects=(
            neg(('clear', 'c1')),
            ('top', 'c1', 'nothing'),

            ('forall',
             ({'component': 'c'}),
             ('when',
              ('top', 'c1', 'c'),
              (('not', ('top', 'c1', 'c')), ('clear', 'c'),)  # assert this
              ),
             ),

            ('forall',
             ({'gridX': 'x1'}),
             ('when',
              ('belongs', 'c1', 'x1'),
              (('not', ('belongs', 'c1', 'x1')), ('-=', ('height', 'x1'), 1),)  # assert this
              ),
             ),

            ('+=', 'displayCurr', 1),
            ('+=', ('visible', 'c1'), 1),
            ('-=', ('onGrid', 'c1'), 1),

        ),
        unique=False,
    )

    move_component = Action(  #### NOW GridX is also a component
        'move_component',
        parameters=(
            ('component', 'c1'),
            ('component', 'c2'),
        ),
        static_preconditions=(('movable', 'c1'),
                              ),
        preconditions=('and',
                       (
                           ('clear', 'c1'),
                           ('clear', 'c2'),
                           ('forall',
                            ({'gridX': 'x'}),
                            ('when',
                             ('belongs', 'c2', 'x'),
                             (('<', ('height', 'x'), gridHeight),)
                             ),
                            ),

                       ),
                       ),
        effects=(
            neg(('clear', 'c2')),
            ('top', 'c1', 'c2'),

            ('forall',
             ({'component': 'c'}),
             ('when',
              ('top', 'c1', 'c'),
              (('not', ('top', 'c1', 'c')), ('clear', 'c'),)  # assert this
              ),
             ),

            ('forall',
             ({'gridX': 'x1'}),
             ('when',
              ('belongs', 'c1', 'x1'),
              (('not', ('belongs', 'c1', 'x1')), ('-=', ('height', 'x1'), 1),)  # assert this
              ),
             ),
            ('forall',
             ({'gridX': 'x2'}),
             ('when',
              ('belongs', 'c2', 'x2'),
              (('belongs', 'c1', 'x2'), ('+=', ('height', 'x2'), 1),)
              ),
             ),
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
            #('locked', 'c'),
            ('-=', 'displayCurr', 1),
            ('+=', ('count', 'c'), 1),
            ('-=', ('visible', 'c'), 1),
        ),
        unique=True,
    )

    domain = Domain((movebox, move_to_station, move_from_station, move_component, unlock_component, place_component, unplace_component, return_component))
    return domain
