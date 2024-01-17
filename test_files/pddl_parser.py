from __future__ import print_function
from time import time
import heapq
from random import randint
import pyddl
from pyddl import listit
import os
from utils import read

## Based on pddlstream

__all__ = ["ParseError", "parse_nested_list"]


class ParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


# Basic functions for parsing PDDL (Lisp) files.
def parse_nested_list(input_file):
    tokens = tokenize(input_file)
    next_token = next(tokens)
    if next_token != "(":
        raise ParseError("Expected '(', got %s." % next_token)
    result = list(parse_list_aux(tokens))
    for tok in tokens:  # Check that generator is exhausted.
        raise ParseError("Unexpected token: %s." % tok)
    return result


def tokenize(input):
    for line in input:
        line = line.split(";", 1)[0]  # Strip comments.
        try:
            line.encode("ascii")
        except UnicodeEncodeError:
            raise ParseError("Non-ASCII character outside comment: %s" %
                             line[0:-1])
        line = line.replace("(", " ( ").replace(")", " ) ").replace("?", " ?")
        for token in line.split():
            yield token.lower()


def parse_list_aux(tokenstream):
    # Leading "(" has already been swallowed.
    while True:
        try:
            token = next(tokenstream)
        except StopIteration:
            raise ParseError("Missing ')'")
        if token == ")":
            return
        elif token == "(":
            yield list(parse_list_aux(tokenstream))
        else:
            yield token


##################################################

def parse_lisp(lisp):
    return pddl_parser.lisp_parser.parse_nested_list(lisp.splitlines())


#Domain = namedtuple('Domain', ['name', 'requirements', 'types', 'type_dict', 'constants',
  #                             'predicates', 'predicate_dict', 'functions', 'actions', 'axioms'])


def parse_domain(domain_pddl):
    return Domain(*parse_domain_pddl(parse_lisp(domain_pddl)))


#Problem = namedtuple('Problem', ['task_name', 'task_domain_name', 'task_requirements', 'objects', 'init',
#                                 'goal', 'use_metric'])


def parse_problem(domain, problem_pddl):
    return Problem(*parse_task_pddl(parse_lisp(problem_pddl), domain.type_dict, domain.predicate_dict))

##################################################

def read_pddl(filename):
    directory = os.path.dirname(os.path.abspath(__file__))
    return read(os.path.join(directory, filename))


def parse_domain_pddl(domain_pddl):
    iterator = iter(domain_pddl)

    define_tag = next(iterator)
    assert define_tag == "define"
    domain_line = next(iterator)
    assert domain_line[0] == "domain" and len(domain_line) == 2
    yield domain_line[1]

    ## We allow an arbitrary order of the requirement, types, constants,
    ## predicates and functions specification. The PDDL BNF is more strict on
    ## this, so we print a warning if it is violated.
    requirements = pddl.Requirements([":strips"])
    the_types = [pddl.Type("object")]
    constants, the_predicates, the_functions = [], [], []
    correct_order = [":requirements", ":types", ":constants", ":predicates",
                     ":functions"]
    seen_fields = []
    first_action = None
    for opt in iterator:
        field = opt[0]
        if field not in correct_order:
            first_action = opt
            break
        if field in seen_fields:
            raise SystemExit("Error in domain specification\n" +
                             "Reason: two '%s' specifications." % field)
        if (seen_fields and
            correct_order.index(seen_fields[-1]) > correct_order.index(field)):
            msg = "\nWarning: %s specification not allowed here (cf. PDDL BNF)" % field
            print(msg, file=sys.stderr)
        seen_fields.append(field)
        if field == ":requirements":
            requirements = pddl.Requirements(opt[1:])
        elif field == ":types":
            the_types.extend(parse_typed_list(
                    opt[1:], constructor=pddl.Type))
        elif field == ":constants":
            constants = parse_typed_list(opt[1:])
        elif field == ":predicates":
            the_predicates = [parse_predicate(entry)
                              for entry in opt[1:]]
            the_predicates += [pddl.Predicate("=",
                                 [pddl.TypedObject("?x", "object"),
                                  pddl.TypedObject("?y", "object")])]
        elif field == ":functions":
            the_functions = parse_typed_list(
                opt[1:],
                constructor=parse_function,
                default_type="number")
    set_supertypes(the_types)
    yield requirements
    yield the_types
    type_dict = dict((type.name, type) for type in the_types)
    yield type_dict
    yield constants
    yield the_predicates
    predicate_dict = dict((pred.name, pred) for pred in the_predicates)
    yield predicate_dict
    yield the_functions

    entries = []
    if first_action is not None:
        entries.append(first_action)
    entries.extend(iterator)

    the_axioms = []
    the_actions = []
    for entry in entries:
        if entry[0] == ":derived":
            axiom = parse_axiom(entry, type_dict, predicate_dict)
            the_axioms.append(axiom)
        else:
            action = parse_action(entry, type_dict, predicate_dict)
            if action is not None:
                the_actions.append(action)
    yield the_actions
    yield the_axioms


def parse_typed_list(alist, default_type="object"):
    result = []
    while alist:
        try:
            separator_position = alist.index("-")
        except ValueError:
            items = alist
            type = default_type
            alist = []
        else:
            items = alist[:separator_position]
            type = alist[separator_position + 1]
            alist = alist[separator_position + 2:]
        for item in items:
            entry = constructor(item, type)
            result.append(entry)
    return result


def parse_action(alist):
    iterator = iter(alist)
    action_tag = next(iterator)
    assert action_tag == ":action"
    name = next(iterator)
    parameters_tag_opt = next(iterator)
    if parameters_tag_opt == ":parameters":
        parameters = parse_typed_list(next(iterator))
        precondition_tag_opt = next(iterator)
    else:
        parameters = []
        precondition_tag_opt = parameters_tag_opt
    if precondition_tag_opt == ":precondition":
        precondition_list = next(iterator)
        if not precondition_list:
            # Note that :precondition () is allowed in PDDL.
            precondition = pddl.Conjunction([])
        else:
            precondition = parse_condition(
                precondition_list, type_dict, predicate_dict)
            precondition = precondition.simplified()
        effect_tag = next(iterator)
    else:
        precondition = pddl.Conjunction([])
        effect_tag = precondition_tag_opt
    assert effect_tag == ":effect"
    effect_list = next(iterator)
    eff = []
    if effect_list:
        try:
            cost = parse_effects(
                effect_list, eff, type_dict, predicate_dict)
        except ValueError as e:
            raise SystemExit("Error in Action %s\nReason: %s." % (name, e))
    for rest in iterator:
        assert False, rest
    if eff:
        return pddl.Action(name, parameters, len(parameters),
                           precondition, eff, cost)
    else:
        return None


domain_pddl = read_pddl('domain.pddl')
problem_pddl = read_pddl('problem.pddl')

aa = parse_nested_list(domain_pddl.splitlines())
for term in aa:
    if term[0] == ':action':
        my_action = parse_action(term)
a = parse_domain_pddl(domain_pddl)
test = 1