from pyddl import Domain, Problem, Action, neg
import random
from collections import defaultdict
from get_precedence import *


def get_objects(nBox, nExtraComponents):
    box_pool = ('box_cir', 'box_tri', 'box_sqr', 'box_cir_2', 'box_tri_2', 'box_sqr_2')
    component_pool = ('circle', 'triangle', 'square', 'circle_2', 'triangle_2', 'square_2')
    objects = dict()
    objects['station'] = ('stat1',)

    objects['box'] = box_pool[:nBox]

    # To only store containers
    objects['container'] = box_pool[:nBox]

    objects['component'] = component_pool[:nBox]

    nCells = nBox + nExtraComponents

    f = [4, 4]
    if nCells < 6 or nCells > 16:
        while is_prime(nCells):
            nCells = nCells + 1
        f = get_factor(nCells)
    elif nCells <= 9:
        f = [3, 3]
    elif nCells <= 12:
        f = [3, 4]
    elif nCells <= 16:
        f = [4, 4]

    '''while nCells % 4 != 0:
        nCells = nCells + 1
    f2 = get_factor(nCells)'''

    [x, y] = f

    objects['gridX'] = list(range(1, x + 1))
    objects['gridY'] = list(range(1, y + 1))
    return objects


def randomize_objects(objects, nExtraComponents):
    # get random order of boxes
    global temp_dict, temp_dict
    boxes_order = list(objects['container'])
    random.shuffle(boxes_order)

    # Set number of components
    compCount = dict()
    for comp in list(objects['component']):
        compCount[comp] = 1
    if nExtraComponents:
        for nC in range(0, nExtraComponents):
            #repeating_component = random.choice(objects['component'])
            repeating_component = objects['component'][nC % len(objects['component'])]
            compCount[repeating_component] = compCount[repeating_component] + 1

    individual_component = []
    compTarget = {}
    for comp in list(objects['component']):
        for i in range(0, compCount[comp]):
            individual_component.append(comp)
    random.shuffle(individual_component)
    for x in objects['gridX']:
        temp_dict = {}
        for y in objects['gridY']:
            if individual_component:
                temp_dict[y] = individual_component.pop()
        compTarget[x] = temp_dict

    return boxes_order, compCount, compTarget


def get_init(objects, compCount, boxes_order, compTarget, nPlatforms, nDisplays, need_box_order=0):
    init = tuple()
    box_literals = []
    boxes = objects['container']
    components = objects['component']
    # Associate components to boxes
    for i in range(0, len(boxes)):  # TODO: separate platforms from boxes
        init = init + (('in', components[i], boxes[i]),)

    # Place components at -x,-y doesn't affect forward search, though it might make reverse search implementation easier
    # for x in compTarget.keys():
    #     for y in compTarget[x].keys():
    #         init = init + (('at', compTarget[x][y], -x, -y),)

    for i in range(0, len(components)):
        init = init + (('=', ('count', components[i]), compCount[components[i]]),)

    for i in range(0, len(components)):
        init = init + (('=', ('visible', components[i]), 0),)
        init = init + (('=', ('onGrid', components[i]), 0),)

    # adding number of displays
    init = init + (('=', 'displayMax', nDisplays),)
    init = init + (('=', 'displayCurr', 0),)

    # arrange boxes
    for i in range(0, len(boxes_order) - 1):
        init = init + (('top', boxes_order[i], boxes_order[i + 1]),)
        if need_box_order:
            box_literals.append(('top', boxes_order[i], boxes_order[i + 1]))
    # place them on platforms
    init = init + (('top', boxes_order[-1], 'I'),)
    if need_box_order:
        box_literals.append(('top', boxes_order[-1], 'I'))

        # clear things that are clear
    init = init + (('clear', boxes_order[0]),)
    if need_box_order:
        box_literals.append(('clear', boxes_order[0]))

    platform_pool = ('I', 'II', 'III', 'IV')
    platforms = platform_pool[:nPlatforms]
    for platform in platforms[1:]:
        init = init + (('clear', platform),)

    # add blank grid and unloading station
    init = init + (('clear', objects['station'][0]),)

    for x in objects['gridX']:
        for y in objects['gridY']:
            # if not(x==4 and (y ==3 or y==4)):
            init = init + (('blank', x, y),)

    if not need_box_order:
        return init
    else:
        return init, box_literals


def get_static_literals(boxes, components):
    static_literals = tuple()
    for box, component in zip(boxes, components):
        static_literals = static_literals + (('movable', box),)
        static_literals = static_literals + (('in', component, box),)

    return static_literals


def get_entropy(compTarget):
    # Run this function only after output_stream['containers'] has been updated, i.e. after running get_problem
    def sign(x):
        if x > 0:
            return 1.
        else:
            return 0.

    def calculate_entropy(target_list):
        entropy = 100
        for i in range(0, len(target_list)):
            temp = 0
            for j in range(0, len(target_list)):
                dx = abs(target_list[i][0] - target_list[j][0])
                dy = abs(target_list[i][1] - target_list[j][1])
                temp = temp + sign(dy * (dx + dy - 1))
            if temp < entropy:
                entropy = temp
        return entropy

    target_list = defaultdict(list)
    for x in compTarget.keys():
        for y in compTarget[x].keys():
            target_list[compTarget[x][y]].append([x, y])

    ind_entropy = {}
    for component in target_list.keys():
        ind_entropy[component] = calculate_entropy(target_list[component])

    entropy = 0
    for c in ind_entropy.keys():
        entropy += (ind_entropy[c]) ** 2
    entropy = entropy / len(ind_entropy)
    return entropy


def get_goal(objects, nPlatforms, compTarget):
    goal = tuple()
    platform_pool = ('I', 'II', 'III', 'IV')
    platforms = platform_pool[:nPlatforms]

    for platform in platforms[1:]:
        goal = goal + (('clear', platform),)

    goal = goal + (('clear', objects['station'][0]),)

    for x in compTarget.keys():
        for y in compTarget[x].keys():
            goal = goal + (('at', compTarget[x][y], x, y),)

    return goal


def get_goal_state(objects, boxes_order, nPlatforms, nDisplays, compTarget, compCount):
    # returns complete goal state (including box positions)
    goal_state = tuple()
    platform_pool = ('I', 'II', 'III', 'IV')
    platforms = platform_pool[:nPlatforms]
    components = objects['component']

    for c, b in zip(objects['component'], objects['container']):  # TODO: separate platforms from boxes
        goal_state += (('in', c, b),)

    # arrange boxes
    for i in range(0, len(boxes_order) - 1):
        goal_state += (('top', boxes_order[i], boxes_order[i + 1]),)

    # place them on platforms
    goal_state += (('top', boxes_order[-1], 'I'),)

    # clear things that are clear
    goal_state += (('clear', objects['station'][0]),)
    goal_state += (('clear', boxes_order[0]),)
    for platform in platforms[1:]:
        goal_state = goal_state + (('clear', platform),)

    goal_state = goal_state + (('clear', objects['station'][0]),)

    for x in compTarget.keys():
        for y in objects['gridY']:
            if y in compTarget[x].keys():
                goal_state = goal_state + (('at', compTarget[x][y], x, y),)
            else:
                goal_state += (('blank', x, y),)

    for i in range(0, len(components)):
        goal_state += (('=', ('count', components[i]), 0),)  # Means no component is now in its box

    for i in range(0, len(components)):
        goal_state += (('=', ('visible', components[i]), 0),)
        goal_state += (('=', ('onGrid', components[i]), compCount[components[i]]),)

    # adding number of displays
    goal_state += (('=', 'displayMax', nDisplays),)
    goal_state += (('=', 'displayCurr', 0),)

    return goal_state



def get_problem(domain, objects, nPlatforms, output_stream, init, goal, boxes_order, compCount):
    static_literals = get_static_literals(objects['container'], objects['component'])
    # init, boxes_order, compCount = get_init(objects, nExtraComponents, nPlatforms, nDisplays)
    # goal = get_goal(objects, nPlatforms, compCount)
    precedence = get_precedence()

    output_stream['Containers'] = []
    for box in boxes_order:
        container = {}
        container['name'] = box
        component = 'nil'
        count = 0
        target = [0, 0]
        for literal in init:
            if literal[0] == 'in' and literal[2] == box:
                component = literal[1]
                count = compCount[component]
                target = []
                for literal_2 in goal:
                    if literal_2[0] == 'at' and literal_2[1] == component:
                        target.append([literal_2[2], literal_2[3]])

        container['count'] = count
        container['components'] = []
        component_dict = {'name': component, 'target': target}
        container['components'].append(component_dict)
        output_stream['Containers'].append(container)

    # add platforms to object dictionary
    #platform_pool = ('I', 'II', 'III', 'IV')
    #platforms = platform_pool[:nPlatforms]
    #objects['box'] = objects['box'] + objects['platform']

    problem = Problem(domain, objects, static_literals, init, goal, precedence)
    return [problem, output_stream]


def is_prime(a):
    x = True
    for i in range(2, a):
        if a % i == 0:
            x = False
            break
    return x


def get_factor(x):
    # This function takes a number and returns set of factor with first factor being smaller than (or equal to) other
    factors = list()
    for i in range(2, x):
        if x % i == 0:
            factors.append(i)
    f1 = min(factors)
    f2 = int(x / f1)

    return [f1, f2]
