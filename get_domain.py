from pyddl import Domain, Problem, Action, neg

# Create a domain for kitting task. Uses the Domain class from pyddl file.

def get_domain(displayMax):
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

    '''NOmovebox_platform = Action(
        'movebox_platform',
        parameters=(
            ('box', 'b1'),
            ('platform', 'p1'),
        ),
        static_preconditions=(('movable', 'b1'),
                              ),
        preconditions=('and',
                       (
                           ('clear', 'b1'),
                           ('clear', 'p1'),

                       ),
                       ),
        effects=(
            ('not',
             ('clear', 'p1'),
             ),
            ('forall',
             ({'box': 'b'}),  # , 'component': 'c'}),  # for all box b
             ('when',
              ('top', 'b1', 'b'),
              (('not', ('top', 'b1', 'b')), ('clear', 'b'),)  # assert this
              ),
             ),
            ('forall',
             ({'platform': 'p'}),  # , 'component': 'c'}),  # for all box b
             ('when',
              ('top', 'b1', 'p'),
              (('not', ('top', 'b1', 'p')), ('clear', 'p'),)  # assert this
              ),
             ),
            ('top', 'b1', 'p1'),
        ),
    )'''

    '''movebox_nope = Action(
        'movebox_nope',
        parameters=(
            ('platform', 'p1'),
            ('platform', 'p2'),
        ),
        preconditions=('and',
                       (
                           ('>', ('n_box', 'p1'), 0),

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
    )'''

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
                           # ('<', 'displayCurr', displayMax),
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

    place_component = Action(
        'place_component',
        parameters=(
            ('component', 'c'),
            ('gridX', 'X'),
            ('gridY', 'Y'),
        ),
        static_preconditions=(),
        preconditions=('and',
                       (
                           ('blank', 'X', 'Y'),
                           ('>', ('visible', 'c'), 0),
                           ('forall',
                            ({'gridY': 'Y1', }),
                            ('when',
                                ('<', 'Y1', 'Y'),
                                neg(('blank', 'X', 'Y1')),
                            ),
                            ),
                       ),
                       ),
        effects=(
            ('+=', ('onGrid', 'c'), 1),
            ('at', 'c', 'X', 'Y'),
            neg(('blank', 'X', 'Y')),
            neg(('at', 'c', 0, 0)),
            ('-=', 'displayCurr', 1),
            ('-=', ('visible', 'c'), 1),
        ),
        unique=False,
    )

    grid_to_display = Action(
        'grid_to_display',
        parameters=(
            ('component', 'c'),
            ('gridX', 'X'),
            ('gridY', 'Y'),
        ),
        static_preconditions=(),
        preconditions=('and',
                       (
                           ('<', 'displayCurr', displayMax),
                           ('at', 'c', 'X', 'Y'),
                           ('forall',
                           ({'gridY': 'Y1', }),
                           ('when',
                            ('>', 'Y1', 'Y'),
                            ('blank', 'X', 'Y1'),
                           ),
                           ),
                       ),
                       ),
        effects=(
            ('-=', ('onGrid', 'c'), 1),
            neg(('at', 'c', 'X', 'Y')),
            ('blank', 'X', 'Y'),
            ('+=', 'displayCurr', 1),
            ('+=', ('visible', 'c'), 1),
        ),
        unique=False,
    )

    grid_to_grid = Action(
        'grid_to_grid',
        parameters=(
            ('gridX', 'X1'),
            ('gridY', 'Y1'),
            ('gridX', 'X2'),
            ('gridY', 'Y2'),
        ),
        static_preconditions=(),
        preconditions=('and',
                       (
                           # ('at', 'c', 'X1', 'Y1'),
                           ('!=', 'X1', 'X2'),
                           neg(('blank', 'X1', 'Y1')),
                           ('blank', 'X2', 'Y2'),
                           ('forall',
                            ({'gridY': 'Y', }),
                            ('when',
                                ('<', 'Y', 'Y2'),
                                neg(('blank', 'X2', 'Y')),
                             ),
                            ),
                           ('forall',
                            ({'gridY': 'Y', }),
                            ('when',
                             ('>', 'Y', 'Y1'),
                             ('blank', 'X1', 'Y'),
                             ),
                            ),
                       ),
                       ),
        effects=(
            ('forall',
             ({'component': 'c'}),
             ('when',
              ('at', 'c', 'X1', 'Y1'),
              (('not', ('at', 'c', 'X1', 'Y1')), ('at', 'c', 'X2', 'Y2'),)  # assert this
              ),
             ),
            ('blank', 'X1', 'Y1'),
            neg(('blank', 'X2', 'Y2')),
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

    error_action = Action(
        'error_action',
        parameters=(),
        static_preconditions=(),
        preconditions=(),
        effects=(),
    )

    redundant_action = Action(
        'redundant_action',
        parameters=(),
        static_preconditions=(),
        preconditions=(),
        effects=(),
    )

    domain = Domain((movebox, move_to_station, move_from_station, unlock_component, place_component, return_component,
                    grid_to_grid, grid_to_display, error_action, redundant_action))
    return domain
