import time

a = ['and', [['top', 'b1', 'b2'], ['clear', 'b3'], ['or', ['adadad', 'b2', 'b3'], ['qw', 'b1'], ], ], ]
a2 = ('and', (('top', 'b11', 'b2'), ('clear', 'b3'), ('or', ('aqq', 'b2', 'b3'), ('qw', 'b1'),),),)
# dic = {'b1':'cir', 'b2':'tri', 'b3':'rec'}

'''
def traverse(sub_list, tree_types=(list, tuple)):
	sub_list_2 = sub_list
	if isinstance(sub_list, tree_types):
		for i in range(0,len(sub_list)):
			if isinstance(sub_list[i], tree_types):
				for subvalue in traverse(sub_list[i]):
					pass
			elif sub_list[i] in dic.keys():
				sub_list_2[i] = dic[sub_list[i]]
	return sub_list_2
'''


def listit(t):
    a = list(map(listit, t)) if isinstance(t, (list, tuple)) else t
    return a


def tupleit(t):
    return tuple(map(tupleit, t)) if isinstance(t, (list, tuple)) else t


def traverse(sub_list, dic, tree_types=(list, tuple)):
    sub_list_2 = sub_list
    for i in range(0, len(sub_list)):
        if isinstance(sub_list[i], tree_types):
            for subvalue in traverse(sub_list[i], dic):
                pass
        elif sub_list[i] in dic.keys():
            sub_list_2[i] = dic[sub_list[i]]
    return tupleit(sub_list_2)


def list2tuple(in_list):
    for i in range(0, len(in_list)):
        if isinstance(in_list[i], list):
            in_list[i] = tuple(in_list[i])
            for subvalue in list2tuple(in_list[i]):
                pass
    return in_list


data = ['aaa', (1, 2, (3, 4, (5, "6"))), (7, 8, 9), (0,), 1, (2, (3, ("4",)))]


# print(list(traverse(a)))
# b = traverse(list(a))
# print(b)

def ground_preconditions(arg_names, args, preconditions):
    namemap = dict()
    for arg_name, arg in zip(arg_names, args):
        namemap[arg_name] = arg
    gr_pr = traverse(listit(preconditions), namemap)
    return tupleit(gr_pr)[0]


init = (
           ('movable', 'box_cir'),
           ('movable', 'box_rec'),
           ('movable', 'box_tri'),

           ('in', 'circle', 'box_cir'),
           ('in', 'triangle', 'box_tri'),
           ('in', 'rectangle', 'box_rec'),

           ('at', 'circle', 0, 0),
           ('at', 'triangle', 0, 0),
           ('at', 'rectangle', 0, 0),

           ('not', ('unlocked', 'circle')),
           ('not', ('unlocked', 'triangle')),
           ('not', ('unlocked', 'rectangle')),

           ('top', 'box_tri', 'box_rec'),
           ('top', 'box_rec', 'box_cir'),
           ('top', 'box_cir', 'I'),
           ('clear', 'box_tri'),
           ('clear', 'II'),
           ('clear', 'III'),
           ('clear', 's'),

           ('blank', 1, 1),  # grid at 1,1 is blank
           ('blank', 1, 2),
           ('blank', 2, 1),
           ('blank', 2, 2),
       ),

preconditions = ('and',
                 (
                     ('clear', 'b1'),
                     ('top', 'b1', 'b2'),
                     ('clear', 'b3'),
                     ('or',
                      (
                          ('top', 'box_cir', 'I'),
                      )
                      ),
                     ('not',
                      (
                          'or',
                          (
                              ('uiyuiyui', 'yuiy'), ('clear', 'aas')
                          ),

                      ),
                      ),
                     ('if',
                      (('clear', 's')),
                      # don't put a comma before the last bracket if there's just one literal, doesn't matter if more than one (CHECK THIS)
                      ('and', (('blank', 2, 2), ('clear', 'III'))),
                      # don't put a comma before the last bracket if there's just one literal
                      )

                 )
                 ),
arg_names = ('b1', 'b2', 'b3')
args = ('box_tri', 'box_rec', 'II')
grounded_preconditions = ground_preconditions(arg_names, args,
                                              preconditions)  # TODO: know why this [0] needs to be here, aka why traverse is returning tuple


print('grounded_preconditions: ', grounded_preconditions)

def is_applicable(init, preconditions):
    GAP = listit(preconditions)

    # apply logical operations here
    if GAP[0] == 'and':
        ans = 1
        for condition in GAP[1]:
            ans = (ans and is_applicable(init, condition))
        return ans

    elif GAP[0] == 'or':
        ans = 0
        for condition in GAP[1]:
            ans = (0 or is_applicable(init, condition))
        return ans

    elif GAP[0] == 'not':
        for condition in GAP[1]:
            return (1 - is_applicable(init, condition))

    elif GAP[0] == 'if':
        return ((1 - is_applicable(init, GAP[1])) or is_applicable(init, GAP[2]))  # if A then B => not(A) or (B)

    elif GAP in listit(init) or GAP in listit(init)[
        0]:  # This is because sometimes listit returns [[list]] and sometimes [list].
        return 1
    else:
        return 0

    '''
	return {
	  'and': (1 and is_applicable(init, condition) for condition in GAP[1]),
	  'not':(-1 * is_applicable(init, condition) for condition in GAP[1]),
	  'or': (0 or is_applicable(init, condition) for condition in GAP[1]),
	  'if': 'TODO'
	  }.get(GAP[0], GAP in listit(init)) #'this is the otherwise case, so check if state.literal is in GAP[1]')'''


qq = is_applicable(init, grounded_preconditions)
print(qq)

# ww = is_applicable((('clear', 'II'),('blank', 1, 2)),(('blank', 1, 1)))
# print(ww)


GA = ['clear', 'box_tri']

LIST = [[['movable', 'box_cir'], ['movable', 'box_rec'], ['movable', 'box_tri'], ['in', 'circle', 'box_cir'],
         ['in', 'triangle', 'box_tri'], ['in', 'rectangle', 'box_rec'], ['at', 'circle', 0, 0],
         ['at', 'triangle', 0, 0],
         ['at', 'rectangle', 0, 0], ['not', ['unlocked', 'circle']], ['not', ['unlocked', 'triangle']],
         ['not', ['unlocked', 'rectangle']],
         ['top', 'box_tri', 'box_rec'], ['top', 'box_rec', 'box_cir'], ['top', 'box_cir', 'I'],
         ['clear', 'box_tri'], ['clear', 'II'],
         ['clear', 'III'], ['clear', 's'], ['blank', 1, 1], ['blank', 1, 2], ['blank', 2, 1], ['blank', 2, 2]]]

a = GA in LIST[0]
# print(a)


'''
def apply_AND(init, GAP):
	#GAP = Grounded Action Preconds
	ans = 1
	for condition in GAP:
		ans = ans and is_applicable(init, condition)
	return ans

def apply_OR(init, GAP):
	#GAP = Grounded Action Preconds
	ans = 1
	for condition in GAP[1]:
		ans = ans and is_applicable(init, condition)
	return ans
'''
