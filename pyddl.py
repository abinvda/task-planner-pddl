"""
Classes and functions that allow creating a PDDL-like
problem and domain definition for planning
"""
from itertools import product
import operator as ops
import time as t
# from pdb import set_trace as bp
from numbers import Number
import string
# import compiler

# Numerical operations
NUM_OPS = {
    '>': ops.gt,
    '<': ops.lt,
    '=': ops.eq,
    '>=': ops.ge,
    '<=': ops.le,
    '!=': ops.is_not
}

LOGIC_OPS = {
    'and': ops.and_,
    'or': ops.or_,
    'not': ops.not_,
}


class Domain(object):

    def __init__(self, actions=()):
        """
        Represents a PDDL-like Problem Domain
        @arg actions : list of Action objects
        """
        self.actions = tuple(actions)

    def ground(self, objects):
        """
        Ground all action schemas given a dictionary
        of objects keyed by type
        """
        grounded_actions = []
        for action in self.actions:
            param_lists = [objects[ty] for ty in action.types]
            param_combos = set()
            for params in product(*param_lists):
                param_set = frozenset(params)
                if action.unique and len(param_set) != len(params):
                    continue
                if action.no_permute and param_set in param_combos:
                    continue
                param_combos.add(param_set)
                grounded_instance = action.ground(objects, *params)
                if grounded_instance.valid == True:
                    grounded_actions.append(grounded_instance)

        return grounded_actions


class Problem(object):
    static_literals = ()

    def __init__(self, domain, objects, static_literals=(), init=(), goal=(), precedence={}):
        """
        Represents a PDDL Problem Specification
        @arg domain : Domain object specifying domain
        @arg objects : dictionary of object tuples keyed by type
        @arg init : tuple of initial state predicates
        @arg goal : tuple of goal state predicates
        @arg precedence: a dict of literals tuples keyed by the action for which those literals must hold true (TODO: add negative literals here too)
        """
        # Class variables, because they are constant for a given problem
        self.objects = objects
        Problem.precedence = precedence
        Problem.static_literals = static_literals

        # Ground actions from domain
        self.grounded_actions = domain.ground(objects)

        self.grounded_actions_dict = self.get_action_dict()
        # Parse Initial State
        # TODO: Negative predicates in the state, though it doesn't seem useful as of now
        predicates = []
        functions = dict()
        for predicate in init:
            if predicate[0] == '=':
                functions[predicate[1]] = predicate[2]
            else:
                predicates.append(predicate)
        self.initial_state = State(predicates, functions)

        predicates = []
        functions = dict()
        for predicate in goal:
            if predicate[0] == '=':
                functions[predicate[1]] = predicate[2]
            else:
                predicates.append(predicate)
        self.goal_state = State(predicates, functions)

        # Parse Goal State
        self.goals = []
        self.num_goals = []
        for g in goal:
            if g[0] in NUM_OPS:
                ng = _num_pred(NUM_OPS[g[0]], *g[1:])
                self.num_goals.append(ng)
            else:
                self.goals.append(g)

        pos_goals = []
        neg_goals = []
        for literal in self.goals:
            if literal[0] == 'not':
                neg_goals.append(literal[1])
            else:
                pos_goals.append(literal)
        self.goals_as_a_list = (pos_goals, neg_goals, self.num_goals)

    def set_initial_state(self, state):
        initial_state = state
        initial_state.predecessor = None
        initial_state.cost = 0
        self.initial_state = initial_state

    def set_goal_state(self, goal_state):
        self.goals = []
        for g in goal_state.predicates:
            if g[0] in NUM_OPS:
                ng = _num_pred(NUM_OPS[g[0]], *g[1:])
                self.num_goals.append(ng)
            else:
                self.goals.append(g)


    def get_action_dict(self):
        action_dict = {}
        for action in self.grounded_actions:
            action_dict[action.sig] = action
        return action_dict

class State(object):

    def __init__(self, predicates, functions, cost=0, predecessor=None):
        """Represents a state for A* search"""
        self.predicates = frozenset(predicates)
        # self.setPredicates = predicates
        # self.listit_predicates = listit(list(self.predicates))
        self.functions = tuple(functions.items())
        self.f_dict = functions
        self.predecessor = predecessor
        self.cost = cost
        self.append_count = 0

    def is_true(self, pos_predicates, neg_predicates, num_predicates):
        try:
            res_func = not(self.f_dict.items() - num_predicates.items())
        except AttributeError:
            res_func = 1
        return (all(p in self.predicates for p in pos_predicates) and
                all(p not in self.predicates for p in neg_predicates) and
                res_func)

    """
        def is_applicable(self, preconditions):
        # GAP = grounded action preconditions
        GAP = listit(preconditions)
        
        #apply logical operations here
        if GAP[0] == 'and':
            ans = 1
            for condition in GAP[1]:
                ans = (ans and is_applicable(self.predicates, condition))
            return ans
        
        elif GAP[0] == 'or':
            ans = 0
            for condition in GAP[1]:
                ans = (0 or is_applicable(self.predicates, condition))
            return ans
        
        elif GAP[0] == 'not':
            return (1 - is_applicable(self.predicates, GAP[1]))
        
        elif GAP[0] == 'if':
            return ((1 - is_applicable(self.predicates, GAP[1])) or is_applicable(self.predicates, GAP[2])) # if A then B => not(A) or (B)
        
        elif GAP in listit(self.predicates) or GAP in listit(self.predicates)[0]: #This is because sometimes listit returns [[list]] and sometimes [list].
            return 1
        
        else:
            return 0
    """

    def is_applicable(self, action):

        applicability = 0
        try:
            parameter_list = action.pred_dict
            # pred_dict = action.pred_dict
            function_dict = self.f_dict
            predicates = self.predicates

            for pred in action.pred_dict:
                if pred in function_dict:
                    parameter_list[pred] = function_dict[pred]
                else:
                    parameter_list[pred] = (pred in predicates)

            applicability = action.eval_applicable(*(parameter_list.values()))  # *(parameter_list1 + parameter_list2))
        except AttributeError:
            if action.name == 'error_action' or action.name == 'redundant_action':
                applicability = 1

        return applicability

    """
    def is_applicable(self, preconditions):
        # GAP = grounded action preconditions
        GAP = preconditions

        # apply logical operations here
        if GAP[0] == 'and':
            ans = 1
            for condition in GAP[1]:
                ans = (ans and self.is_applicable(condition))
                if ans == 0:
                    break
            return ans

        elif GAP[0] == 'or':
            ans = 0
            for condition in GAP[1]:
                ans = (ans or self.is_applicable(condition))
                if ans == 1:
                    break
            return ans

        elif GAP[0] == 'not':
            return (1 - self.is_applicable(GAP[1]))

        elif GAP[0] == 'when':
            return ((1 - self.is_applicable(GAP[1])) or self.is_applicable(GAP[2]))  # if A then B => not(A) or (B)

        elif GAP[0] in NUM_OPS:
            operation = NUM_OPS[GAP[0]]
            return operation(GAP[1], GAP[2])

        elif GAP in self.listit_predicates:  # or GAP in listit(list(self.predicates))[0][0]: #This is because sometimes listit returns [[list]] and sometimes [list].
            return 1

        else:
            return 0

    """

    def apply(self, action, monotone=False):
        """
        Apply the action to this state to produce a new state.
        If monotone, ignore the delete list (for A* heuristic)
        """
        new_preds = set(self.predicates)  # set(tupleit(listit(self.setPredicates)))
        new_preds |= set(action.add_effects)
        if not monotone:
            new_preds -= set(action.del_effects)

        new_functions = dict()

        new_functions.update(self.functions)
        for function, value in action.num_effects:
            new_functions[function] += value

        for cond in action.conditional_effects:
            if cond[0] in self.predicates:
                for then_effect in cond[1]:
                    if then_effect[0] == 'not':
                        a = set()
                        a.add(then_effect[1])
                        new_preds -= a
                    elif then_effect[0] == '+=':
                        new_functions[then_effect[1]] += then_effect[2]
                    elif then_effect[0] == '-=':
                        new_functions[then_effect[1]] -= then_effect[2]
                    else:
                        a = set()
                        a.add(then_effect)
                        new_preds |= a  # MORE workaround
            # print('cond: ', cond)
        return State(new_preds, new_functions, self.cost + 1, (self, action))

    def check_apply_action(self, grounded_action):  # check the applicability and then apply action
        if self.is_applicable(grounded_action):
            new_state = self.apply(grounded_action)
            return new_state

    def plan(self):
        """
        Follow backpointers to successor states
        to produce a plan.
        """
        plan = []
        succ = []
        n = self
        succ.append(n)
        while n.predecessor is not None:
            plan.append(n.predecessor[1])
            succ.append(n.predecessor[0])
            n = n.predecessor[0]
        plan.reverse()
        succ.reverse()
        return [plan, succ]


    def plan_R(self, problem):
        """
        Follow backpointers to predecessor (in this case will be successors) states
        to produce a plan.
        """
        plan = []
        succ = []
        n = self
        succ.append(n)
        while n.predecessor is not None:
            # plan.append(n.predecessor[1])
            succ.append(n.predecessor[0])
            next_state = n.predecessor[0]
            # Apply all applicable actions to get successors
            successors = set(n.apply(action) for action in problem.grounded_actions if n.is_applicable(action))
            for successor in successors:
                if successor == next_state:
                    plan.append(successor.predecessor[1])
                    break
            n = n.predecessor[0]
        # plan.reverse()
        # succ.reverse()
        return [plan, succ]


    # Implement __hash__ and __eq__ so we can easily
    # check if we've encountered this state before

    def __hash__(self):
        return hash((self.predicates, self.functions))

    def __eq__(self, other):
        return ((self.predicates, self.functions) ==
                (other.predicates, other.functions))

    def __str__(self):
        return ('Predicates:\n%s' % '\n'.join(map(str, self.predicates))
                + '\nFunctions:\n%s' % '\n'.join(map(str, self.functions)))

    def __lt__(self, other):
        return hash(self) < hash(other)


class Action(object):
    """
    An action schema
    """

    def __init__(self, name, parameters=(), duration=1, static_preconditions=(), preconditions=(), effects=(),
                 unique=True, no_permute=False):
        """
        A PDDL-like action schema
        @arg name : action name for display purposes
        @arg parameters : tuple of ('type', 'param_name') tuples indicating
                          action parameters
        @arg precondtions : tuple of preconditions for the action
        @arg effects : tuple of effects of the action
        @arg unique : if True, only ground with unique arguments (no duplicates)
        @arg no_permute : if True, do not ground an action twice with the same
                          set of (permuted) arguments
        """
        self.name = name
        if len(parameters):
            self.types, self.arg_names = zip(*parameters)
        else:
            self.types = tuple()
            self.arg_names = tuple()
        self.preconditions = preconditions
        self.static_preconditions = static_preconditions
        self.effects = effects
        self.unique = unique
        self.no_permute = no_permute

    def resolve_adl(self, objects, mode):
        # resolves (expands) ADL conditions: 'forall' and 'exists'
        # mode is effects or preconditions, tells what to ground
        predicates = ()
        if mode == 'preconditions':
            predicates = self.preconditions
        elif mode == 'effects':
            predicates = self.effects
        resolved_conditions = resolve_adl_iterate(objects, listit(predicates), mode)

        return tupleit(resolved_conditions)

    def ground(self, objects, *args):
        if self.name == 'error_action' or self.name == 'redundant_action':
            self.preconditions = []
            self.effects = []
        else:
            self.preconditions = self.resolve_adl(objects, 'preconditions')
            self.effects = self.resolve_adl(objects, 'effects')
        return _GroundedAction(self, *args)

    def __str__(self):
        arglist = ', '.join(['%s - %s' % pair for pair in zip(self.arg_names, self.types)])
        return '%s(%s)' % (self.name, arglist)


class _GroundedAction(Problem):
    """
    An action schema that has been grounded with objects
    """

    def __init__(self, action, *args):
        self.name = action.name
        grounded = _grounder(action.arg_names, args)
        # grounded Action Signature
        self.sig = grounded((self.name,) + action.arg_names)
        # grounded Preconditions
        self.grounded_preconditions = grounded(action.preconditions)
        grounded_static_preconditions = grounded(action.static_preconditions)

        static_literals = Problem.static_literals
        precedence = Problem.precedence
        # Add precedence conditions, if any, to the action preconditions
        self.valid = 1
        if bool(static_literals) and bool(action.static_preconditions):
            for i in grounded_static_preconditions:
                self.valid = self.valid * (i in static_literals)
        if self.valid:
            #if bool(precedence):
             #   if self.sig in precedence.keys():
              #      self.grounded_preconditions = self.grounded_preconditions[0], self.grounded_preconditions[1] + \
               #                                   precedence[self.sig]
                    # for precond in precedence[self.sig]:
                    # self.grounded_preconditions = ('and', (self.grounded_preconditions, precond))  # this is for generalised (nestable) preconditions

            # self.listit_grounded_preconditions = listit(self.grounded_preconditions)

            #self.and_preconditions = []
            #self.or_preconditions = []
            #self.not_preconditions = []
            #self.when_preconditions = []
            self.num_preconditions = {}

            #self.sort_preconditions(self.grounded_preconditions, 'and')

            self.predicate_list = self.get_predicate_list(self.grounded_preconditions)
            self.pred_dict = {}
            for j in range(0, len(self.predicate_list)):
                self.pred_dict[self.predicate_list[j]] = string.ascii_lowercase[j]

            if not (self.name == 'error_action' or self.name == 'redundant_action'):
                self.parsed = parse_preconditions(self.grounded_preconditions, self.pred_dict)

                #self.check_applicable = parse_applicable(self.parsed, self.predicate_list)

                self.eval_applicable = eval_compile(self.parsed, list(self.pred_dict.values()))

                for pre in action.preconditions[1]:
                    if pre[0] in NUM_OPS:
                        operands = [0, 0]
                        for i in range(2):
                            if type(pre[i + 1]) == int:
                                operands[i] = pre[i + 1]
                            else:
                                operands[i] = grounded(pre[i + 1])
                        np = _num_pred(NUM_OPS[pre[0]], *operands)
                        self.num_preconditions[grounded(pre)] = np

                # Grounded Effects
            self.grounded_effects = grounded(action.effects)

            self.add_effects = []
            self.del_effects = []
            self.conditional_effects = []
            self.num_effects = []

            for effect in self.grounded_effects:
                # print('382:  effect: ', effect)
                if effect[0] == 'not':
                    self.del_effects.append(grounded(effect[1]))
                elif effect[0] == 'when':
                    self.conditional_effects.append((effect[1], effect[2]))
                elif effect[0] == '+=':
                    function = grounded(effect[1])
                    value = effect[2]
                    self.num_effects.append((function, value))
                elif effect[0] == '-=':
                    function = grounded(effect[1])
                    value = -effect[2]
                    self.num_effects.append((function, value))
                else:
                    self.add_effects.append(grounded(effect))

    def get_predicate_list(self, conditions):
        predicate_list = ()

        if not conditions:
            return predicate_list
        elif conditions[0] == 'not':
            predicate_list = predicate_list + (conditions[1],)
        elif conditions[0] in LOGIC_OPS:
            for cond in conditions[1]:
                predicate_list = predicate_list + self.get_predicate_list(cond)
        elif conditions[0] == 'when':
            for cond in conditions[1:]:
                predicate_list = predicate_list + self.get_predicate_list(cond)
        elif conditions[0] in NUM_OPS:
            if not isinstance(conditions[1], Number):
                predicate_list = predicate_list + (conditions[1],)
            else:
                return ()
        else:
            predicate_list = predicate_list + (conditions,)

        return predicate_list

    """predicate_list = []

    if isinstance(conditions, Number):
        t = 1
    elif conditions[0] == 'not':
        predicate_list.append(str((conditions[1])))
    elif conditions[0] in LOGIC_OPS:
        for cond in conditions[1]:
            predicate_list.append(self.get_predicate_list(cond)[0])
    elif conditions[0] == 'when':
        for cond in conditions[1:]:
            predicate_list.append(self.get_predicate_list(cond)[0])
    elif conditions[0] in NUM_OPS:
        if not isinstance(conditions[1], Number):
            predicate_list.append(str((conditions[1])))
        else:
            return []
    else:
        predicate_list.append(str((conditions)))

    return predicate_list"""


    def __str__(self):
        arglist = ', '.join(map(str, self.sig[1:]))
        return '%s(%s)' % (self.sig[0], arglist)

    def sort_preconditions(self, precondition, cond_type):
        # WHEN = IF condition
        # GAP = grounded action preconditions
        GAP = precondition
        # if precondition[0] in NUM_OPS:
        #   return
        if self.name == 'place_component':
            test = 1

        # There are 4 types of preconditions: AND, OR, IF, NOT
        if GAP[0] == 'and' or GAP[0] == 'or':
            for condition in GAP[1]:
                self.sort_preconditions(condition, GAP[0])

        # elif GAP[0] == 'not':
        #   self.not_preconditions.append(GAP[1])

        elif GAP[0] == 'when':
            self.when_preconditions.append((GAP[1], GAP[2]))

        elif cond_type == 'and':
            self.and_preconditions.append(precondition)

        elif cond_type == 'or':
            self.or_preconditions.append(precondition)

        return


def parse_preconditions(condition, pred_dict):

    if isinstance(condition, Number):
        return str(condition)
    elif condition[0] == 'and':
        result = '1'
        for sub_cond in condition[1]:
            result = " ( " + result + " ) " + " and " + " ( " + str(parse_preconditions(sub_cond, pred_dict)) + " ) "
        return result
    elif condition[0] == 'or':
        result = '0'
        for sub_cond in condition[1]:
            result = " ( " + result + " ) " + " or " + " ( " + str(parse_preconditions(sub_cond, pred_dict)) + " ) "
        return result
    elif condition[0] == 'not':
        return " not " + " ( " + str(parse_preconditions(condition[1], pred_dict)) + " ) "
    elif condition[0] == 'when':
        return " not " + " ( " + str(parse_preconditions(condition[1], pred_dict)) + " ) " + " or " + " ( " + str(parse_preconditions(condition[2], pred_dict)) + " ) "

    elif condition[0] in NUM_OPS:
        return " ( " + str(parse_preconditions(condition[1], pred_dict)) + " ) " + condition[0] + " ( " + str(parse_preconditions(condition[2], pred_dict)) + " ) "
    else:
        return pred_dict[condition]


def eval_compile(conditions_string, predicate_list):
    #compiled = compiler.compile(conditions_string, '<string>', 'eval')
    return eval("lambda %s: %s" % (", ".join(predicate_list), conditions_string))


def parse_applicable(conditions_string, predicate_list):

    def temp_func(state):
        cond = conditions_string
        for predicate in predicate_list:
            if predicate in state.f_dict:
                cond = cond.replace(str(predicate), str(state.f_dict[predicate]))
            else:
                cond = cond.replace(str(predicate), str(predicate in state.predicates))
        return eval(cond)

    return temp_func

"""def eval_applicable(action, state):
    if isinstance(action, _GroundedAction):
        condition = action.grounded_preconditions
        predicate_list = action.predicate_list
        num_preconditions = action.num_preconditions
        if action.name == 'grid_to_grid':
            t = 1
    else:
        condition = action[0]
        predicate_list = action[1]
        num_preconditions = action[2]

    if isinstance(condition[0], tuple):
        answer = []
        for cond in condition:
            if cond[0] in NUM_OPS:
                t = 1
            if cond in predicate_list:
                answer.append(cond in state.predicates)
            else:
                answer.append(eval_applicable([cond, predicate_list, num_preconditions], state))

        return answer

    elif condition[0] == 'and':
        return all(eval_applicable([condition[1], predicate_list, num_preconditions], state))
    elif condition[0] == 'or':
        return any(eval_applicable([condition[1], predicate_list, num_preconditions], state))
    elif condition[0] == 'not':
        return not eval_applicable([condition[1], predicate_list, num_preconditions], state)
    elif condition[0] == 'when':
        return not eval_applicable([condition[1], predicate_list, num_preconditions], state) or eval_applicable([condition[2], predicate_list, num_preconditions], state)

    elif condition[0] in NUM_OPS:
        if isinstance(condition[1], Number):
            return NUM_OPS[condition[0]](condition[1], condition[2])
        else:
            np = num_preconditions[condition]
            return np(state)
    elif condition in predicate_list:
        return condition in state.predicates"""


def resolve_adl_iterate(objects, sub_conditions, mode):
    resolved_conditions = []
    if mode == 'preconditions':
        resolved_conditions = sub_conditions
        for i in range(0, len(sub_conditions)):
            # print('237: ', i, '  :', sub_conditions[i])
            if isinstance(sub_conditions[i], list):  # or isinstance(sub_conditions, list):
                if sub_conditions[i][0] == 'forall':
                    namemap = dict()
                    for obj in sub_conditions[i][1].keys():
                        namemap[sub_conditions[i][1].get(obj)] = objects.get(obj)
                    resolved_conditions[i] = resolve_forall(sub_conditions[i], namemap,
                                                            mode)  # this should give the AND list of predicates
                elif sub_conditions[i][0] == 'exists':
                    namemap = dict()
                    for obj in sub_conditions[i][1].keys():
                        namemap[sub_conditions[i][1].get(obj)] = objects.get(obj)
                    resolved_conditions[i] = resolve_exists(sub_conditions[i], namemap)
                else:
                    for v in resolve_adl_iterate(objects, sub_conditions[i], mode):
                        pass

    elif mode == 'effects':
        resolved_conditions = []  # sub_conditions
        for i in range(0, len(sub_conditions)):
            # print('344: ', i, '  :', sub_conditions[i])
            if isinstance(sub_conditions[i], list):  # or isinstance(sub_conditions, list):
                if sub_conditions[i][0] == 'forall':
                    namemap = dict()
                    for obj in sub_conditions[i][1].keys():
                        namemap[sub_conditions[i][1].get(obj)] = objects.get(obj)
                    resolved_conditions.extend(
                        resolve_forall(sub_conditions[i], namemap, mode))  # this should give the AND list of predicates
                elif sub_conditions[i][0] == 'exists':
                    namemap = dict()
                    for obj in sub_conditions[i][1].keys():
                        namemap[sub_conditions[i][1].get(obj)] = objects.get(obj)
                    resolved_conditions.append(resolve_exists(sub_conditions[i], namemap))
                else:
                    resolved_conditions.append(sub_conditions[i])
                    for v in resolve_adl_iterate(objects, sub_conditions[i], mode):
                        pass

    return resolved_conditions


def resolve_forall(conditions, namemap, mode):
    # should return an and list with all the forall predicates stated
    resolved = []
    pred = conditions[2]

    for o in namemap.keys():
        changeVar = dict()
        for v in namemap[o]:
            changeVar[o] = v
            resolved.append(traverse(tupleit(pred), changeVar))

    if mode != 'effects':
        resolved = ['and', ] + [resolved]

    return resolved


def resolve_exists(conditions, namemap):
    resolved = []
    pred = conditions[2]

    for o in namemap.keys():
        changeVar = dict()
        for v in namemap[o]:
            changeVar[o] = v
            resolved.append(traverse(tupleit(pred), changeVar))

    resolved = ['or', ] + [resolved]
    return resolved


def _num_pred(op, x, y):
    """
    Returns a numerical predicate that is called on a State.
    """

    def predicate(state):
        operands = [0, 0]
        for i, o in enumerate((x, y)):
            if type(o) == int:
                operands[i] = o
            else:
                operands[i] = state.f_dict[o]
        return op(*operands)

    return predicate


def neg(literal):
    """
    Makes the given effect a negative (delete) effect, like 'not' in PDDL.
    """
    return ('not', literal)


def listit(t):
    a = list(map(listit, t)) if isinstance(t, (list, tuple)) else t
    return a


def tupleit(t):
    return tuple(map(tupleit, t)) if isinstance(t, (list, tuple)) else t


def _grounder(arg_names, args):
    """
    Returns a function for grounding predicates and function symbols
    """
    namemap = dict()
    for arg_name, arg in zip(arg_names, args):
        namemap[arg_name] = arg

    def _ground_conditions(conditions):
        # replace all variables in preconditions according to dictionary namemap
        gr = traverse(tupleit(conditions), namemap)
        return tupleit(gr)

    """
    def _ground_by_names(predicate):
        # predicate is every predicate grounded starting from grounded action name
        # then precond literals then effect literals
        return predicate[0:1] + tuple(namemap.get(arg, arg) for arg in predicate[1:])
    """

    return _ground_conditions


def traverse(sub_list, grounded_objects_dict, tree_types=(list, tuple)):
    """
    Replaces variables with grounded objects.
    sub_list = list containing variables
    grounded_objects_dict = dictionary stating which variable to replace with which object/value
    """
    updated_list = listit(sub_list)
    for i in range(0, len(sub_list)):
        if isinstance(sub_list[i], tree_types):
            updated_list[i] = traverse(sub_list[i], grounded_objects_dict)
        elif sub_list[i] in grounded_objects_dict.keys():
            updated_list[i] = grounded_objects_dict[sub_list[i]]
    return updated_list
