def get_heuristic(problem, compTarget, objects):
    clear_platform_cost = clear_platform_heuristic(problem)
    componentCost = componentCost_heurictic(compTarget, objects)

    def total_heuristic(state):
        dist = 1 * componentCost(state) + 1 * clear_platform_cost(state)
        # dist = 1 * distance_heuristic(state) + 1 * box_mismatch_heuristic(state)
        return dist

    return total_heuristic


def get_reverse_heuristic(initial_state, comp_init, objects):
    # this compTarget is the component dictionary of the given state (whose 'distance from start' we are estimating)
    # the heuristic will estimate distance from goal_state to a given state
    box_mismatch_count = box_mismatch_heuristic(box_position(initial_state.predicates))
    component_mismatch_count = componentCost_reverse_heurictic(objects, reverse=1)

    def reverse_heuristic(state):
        dist = 0 * box_mismatch_count(state) + 1 * component_mismatch_count(state)
        return dist

    return reverse_heuristic


def componentCost_heurictic(compTarget, objects, reverse=0):
    temp_dict = {}
    for box, component in zip(objects['container'], objects['component']):
        temp_dict[component] = box

    def componentCost(state):
        dist = 0
        dont_count_twice = 0
        for comp in compTarget.keys():
            box_needed = 0
            for tar in compTarget[comp]:
                if ('at', comp, tar[0], tar[1]) not in state.predicates:  # If component isn't placed at target location
                    dist += 1
                    for comp2 in compTarget:
                        for tar2 in compTarget[comp2]:
                            if (tar2[0] == tar[0]) and ((tar2[1] == tar[1]+1) or (tar2[1] == tar[1]+2)) and (('at', comp2, tar2[0], tar2[1]) in state.predicates):
                                # If different comp is placed correctly on top of its location
                                dist += 1

            # for targets in zip(compTarget[comp], compTarget[comp][1:] + [compTarget[comp][0]]):
            #     if (targets[0][0] == targets[1][0]) and (abs(targets[0][1] - targets[1][1]) == 2) and (
            #             ('at', comp, targets[0][0], min(targets[1][1], targets[0][1])) not in state.predicates):
            #         dist += 1

                    # if ('blank', tar[0], tar[1]) not in state.predicates:  # If different comp is at it's target
                    #     dist += 1
            if state.f_dict[('count', comp)] > 0:  # If component is not unlocked
                dist += state.f_dict[('count', comp)]

                box_comp = temp_dict[comp]  # If the box(container) is required to unlock a component
                if ('top', box_comp, 'stat1') not in state.predicates:
                    dist += 1
                    # if ('clear', 'stat1') not in state.predicates and not dont_count_twice:
                    #     dist += 1
                    #     dont_count_twice = 1
                    for other_box in objects['container']:
                        if ('top', other_box, box_comp) in state.predicates:
                            dist += 1
                            for yet_another_box in objects['container']:
                                if ('top', yet_another_box, other_box) in state.predicates:
                                    dist += 1
                                    for yet_yet_another_box in objects['container']:
                                        if ('top', yet_yet_another_box, yet_another_box) in state.predicates:
                                            dist += 1
                                            for yet_yet_yet_another_box in objects['box']:
                                                if ('top', yet_yet_yet_another_box, yet_yet_another_box) in state.predicates:
                                                    dist += 1
                                                    break
                                            break
                                    break
                            break

        return dist
    return componentCost


def componentCost_reverse_heurictic(objects, reverse=1):
    temp_dict = {}
    for box, component in zip(objects['container'], objects['component']):
        temp_dict[component] = box

    def componentCost(state):
        dist = 0
        for pred in state.predicates:
            if pred[0] == 'at':
                dist += 1

            # for targets in zip(compTarget[comp], compTarget[comp][1:] + [compTarget[comp][0]]):
            #     if (targets[0][0] == targets[1][0]) and (abs(targets[0][1] - targets[1][1]) == 2) and (
            #             ('at', comp, targets[0][0], min(targets[1][1], targets[0][1])) not in state.predicates):
            #         dist += 1

                    # if ('blank', tar[0], tar[1]) not in state.predicates:  # If different comp is at it's target
                    #     dist += 1
        once = 1
        for comp in objects['component']:
            box_needed = 0
            # if reverse:
            if state.f_dict[('onGrid', comp)] + state.f_dict[('visible', comp)] > 0:  # If component is not in its box
                dist += state.f_dict[('onGrid', comp)] + state.f_dict[('visible', comp)]
                box_needed = 1
            # else:
            #     if state.f_dict[('count', comp)] > 0:  # If component is not unlocked
            #         dist += state.f_dict[('count', comp)]
            #         box_needed = 1
            if box_needed:
                box = temp_dict[comp]  # If the box(container) is required to unlock a component
                if ('top', box, 'stat1') not in state.predicates:
                    dist += 1
            #         # if ('clear', 'stat1') not in state.predicates and once:
            #         #     dist += 1
            #         #     once = 0
            #         for other_box in objects['container']:
            #             if ('top', other_box, box) in state.predicates:
            #                 dist += 1
            #                 for yet_another_box in objects['container']:
            #                     if ('top', yet_another_box, other_box) in state.predicates:
            #                         dist += 1
            #                         for yet_yet_another_box in objects['container']:
            #                             if ('top', yet_yet_another_box, yet_another_box) in state.predicates:
            #                                 dist += 1
            #                                 for yet_yet_yet_another_box in objects['box']:
            #                                     if ('top', yet_yet_yet_another_box, yet_yet_another_box) in state.predicates:
            #                                         dist += 1
            #                                         break
            #                                 break
            #                         break
            #                 break
            #
            else:
                if ('top', temp_dict[comp], 'stat1') in state.predicates:
                    dist += 1
        return dist
    return componentCost


def predicate_mismatch_heuristic(goals):  # Used in function simple_optimality_check
    def predicate_cost(state):
        dist = 0
        for pred in goals:
            if pred[0] != 'clear' and pred[0] != 'blank' and pred not in state.predicates:
                dist += 1
        return dist
    return predicate_cost


def clear_platform_heuristic(goal):

    def clear_platform_cost(state):
        dist = 0
        for g in goal:
            if g[0] == 'clear' and g not in state.predicates:  # and g[1] != 'stat1'
                dist = dist + 1
        return dist

    return clear_platform_cost


def box_position(state):
    boxDict = {}
    for pq in state:
        if pq[0] == 'top':
            boxDict[pq[1]] = (pq[2])
    return boxDict


def box_mismatch_heuristic(goal_boxDict):
    def box_mismatch_count(state):
        state_boxDict = box_position(state.predicates)
        dist = 0
        # print(state_boxDict)
        for k in goal_boxDict.keys():
            # print(state_boxDict[k])
            # print(goal_boxDict[k])
            if goal_boxDict[k] != state_boxDict[k]:
                dist += 1
        return dist
    return box_mismatch_count


