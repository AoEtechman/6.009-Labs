#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def deep_copy_list(lst):
    """
    Takes an input list and returns a deep copy of that list

    inputs:
        lst: list
    return:
        list: deep copy of input list
    """
    if type(lst) == list:
        return [deep_copy_list(elem) for elem in lst]
    return lst


def formula_trimmer(formula, variable, boolean):
    """
    Takes a CNF formula and trims it based on a (variable, boolean) pairing.
    Trimming is taking the (variable, boolean) pairing and applying it to the CNF function. 
    A new function will result from applying the (variable, boolean) pairing, and we return this new function

    inputs:
        formula: a CNF formula
        variable: a variable in the CNF formula
        boolean: True or False
    
    returns:
        a new CNF function
    """
    formula_copy = deep_copy_list(formula)
    # if we have satisfied all of the clauses, return True,
    #which means we have a solution to cnf
    if formula == []:
        return True
    for clause in formula_copy.copy():
        if (variable, boolean) in clause:
            formula_copy.remove(clause) # if argument is in the clause, the clause has been satisfied
            if formula_copy == []: #check again if we have a soltuion and return true if so
                return True
        else:
            for literal in clause.copy(): # if argument is not in clause, check if variable is in a literal in the clause
                if variable == literal[0]: # if varaible is in a literal in the clause, remove that literal
                    # this means that we have a argument that disatisfies that literal
                    clause.remove(literal)
            if clause == []: # if a clause is empty, this means we have no more valid moves that satisfy contraint
                # so we have produced a losing solution. return None
                return None
    return formula_copy


def choose_guess_space(formula):
    """
    This function creates a guess space based on the length of a clause
    if a clause is length 1, then its guess space is the guess that would satisfy
    that clause.

    input:
        formula: CNF formula
    
    return:
        guess space: [True, False] or just False or True
    """
    if len(formula[0]) == 1:# if unit clause
        literal = formula[0][0]
        return([literal[1]])# return boolean that satisfies
    else:
        return [True, False]

def satisfying_assignment(formula, bool_dict = None, level = 0):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if formula == []: # if formula is empty, no satisfying assignment
        return {}
    if level == 0: # if we are at the first level of recursion, create a satisfying assignment dictionary
        bool_dict = {}
    # find all unit clauses and propogate their effects through the CNF formula(ie trimm formula by each unit clause)
    for clause in formula:
        if len(clause) == 1:# if unit clause
            bool_dict[clause[0][0]] = clause[0][1]
            formula = formula_trimmer(formula, clause[0][0], clause[0][1])
            if formula == None: # if no solution, return none
                return None
            elif formula == True: # if satisfied, return satisfying dict
                return bool_dict
    literal = formula[0][0] 
    guess_space = choose_guess_space(formula)
    for guess in guess_space:
        new_formula = formula_trimmer(formula, literal[0], guess) # trim formula
        if new_formula == True: # if solution satisfied, update satisfied dictionary
            bool_dict[literal[0]] = guess
            return bool_dict # return the bool dictionary
        if new_formula != None: # if we can still satisfy formula
            bool_dict[literal[0]] = guess # update satisfied dictionary
            if satisfying_assignment(new_formula, bool_dict, level + 1): # if a solution exists, return the satisfied dict
                return bool_dict
            else:
                continue
        if new_formula == None: # if out guess did not satisfy the formula, try next guess 
            continue
    return None # back track
    

            
    
def create_room_rules(lst, length, level, new_list = []):
    """
    This function takes all of the rooms and ensures that the rooms never have more students than they can hold

    inputs:
        lst: a list
        length: desired length of return lists
        new_list: new_list that we add to on each iteration

    returns:
        list: a list of lists
    """
    if level == 0: #if we have reached desired length, return sublist
        new_list3 = [new_list]
        return new_list3
    rules = []
    for i in range(len(lst)):
        new_list2 = deep_copy_list(new_list)
        new_list2.append(lst[i])
        rules += create_room_rules(lst[i+1:], length, level-1, new_list2) # add all of the sublists together, return this total list
    return rules

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    room_limits = [] 
    output = []
    inner2 = []
    s = set()
    rooms = student_preferences.values()
    # generate a set of all of the rooms in our scheduling case
    for room in rooms:
        for room1 in room:
            s.add(room1)
    # generate rules for students in desired sections
    for key in student_preferences:
        inner = []
        for vals in student_preferences[key]: 
            out = key+"_"+vals # create format "student_preference"
            inner.append((out, True))# they can be in this room so true
        output.append(inner)# add all clauses together
        # generate rules for each student in only one room
        for room in s:# for each room
            # generate literal with all of the room pairings being set to false for each person
            # essentially, they cannot be in two rooms at a time
            for room2 in s:
                if room != room2:
                    out = []
                    out.append((key+"_"+room2, False)) 
                    out.append((key+"_"+room, False))
                    inner2.append(tuple(out))
    inner2 = [list(elem) for elem in inner2]# create sub rules list with clauses
    # generate rules for no room over max capacity
    for loc in room_capacities:
        out2 = []
        n = room_capacities[loc]
        #generate list with each student and all of the rooms
        for person in student_preferences:
            out2.append((person+"_"+loc, False))
        # calculates rules that ensure the rooms dont have more than they 
        # can hold
        room_limits += create_room_rules(out2, n+1, n+1) 
    # add all of the rules togther
    rules = room_limits+output + inner2
    return rules




if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
#     formula = [[("a", True)], [("b", False)]]
#     formula2 = [[("b", False)]]
#     formula3 = [
#     [('a', True), ('b', True), ('c', True)],
#     [('a', False), ('f', True)],
#     [('d', False), ('e', True), ('a', True), ('g', True)],
#     [('h', False), ('c', True), ('a', False), ('f', True)],
# ]
    # print(formula_trimmer(formula3, "a", True))
    # [[("f", True)], [("h", False), ("c", True), ("f", True)]]
    # formula = [[('a', True), ('a', False)], [('b', True), ('a', True)], [('b', True)], [('b', False), ('b', False), ('a', False)], [('c', True), ('d', True)], [('c', True), ('d', True)]]
    # print(satisfying_assignment(formula, {}))
    # formula = [[('b', True)], [('b', False), ('b', False)], [('c', True), ('d', True)], [('c', True), ('d', True)]]
    # print(formula_trimmer(formula, "b", True))
    # students = {'student0': ['session0', 'session1'], 'student1': ['session1', 'session2'], 'student2': ['session2']}
    # sessions = {'session0': 2, 'session1': 1, 'session2': 2}
    # haha = boolify_scheduling_problem(students, sessions)
    # sched = satisfying_assignment(haha)
    # for var, val in sched.items():
    #     if val:
    #         student, session = var.split("_")
    #         # print(student, session)
    pass


