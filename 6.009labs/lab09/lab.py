"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
from unittest import result
sys.setrecursionlimit(10_000)


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            if x == "@t":
                return True
            elif x == "@f":
                return False
            return x


def tokenize(str_input):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """
    token = []
    nums = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
    invalid = {" ", "\n", ")", "("}
    while str_input:
        
        if str_input[0] not in invalid:
            tot = ""
            # if we have reached the beggining of a comment, find where the commment ends
            if str_input[0] == "#":
                try:
                    index = str_input.find("\n")
                    if index == -1:
                        str_input = []
                        return token
                    else:
                        str_input = str_input[index + 1:]
                except: # we have reached the end of the expression or string     
                    str_input = []
                    return token
            # if not a comment and not an invalid character, keep on appending to our return statement untill we have reached the end of the expression
            else:
                try:
                    while str_input[0] not in invalid:
                        tot += str_input[0]
                        str_input = str_input[1:]
                    token.append(tot)    
                except:
                    str_input = [] 
                    token.append(tot)   
                    return token
        # if the character is a parenthesis, add the character to our output
        elif str_input[0] != " " and str_input[0] != '\n':
            token.append(str_input[0])
            str_input = str_input[1:]
        else: # if it is a space or new line do not add to return list
            str_input = str_input[1:]
    return token



def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    # if the number of opening and closing parenthesis are not the same, raise a syntax error
    open_paren_count = 0
    close_paren_count = 0
    for elem in tokens:
        if elem == "(":
            open_paren_count += 1
        elif elem == ")":
            close_paren_count += 1
    if open_paren_count != close_paren_count:
        raise CarlaeSyntaxError
    # if there are no parenthesis in token and the token is not a single character, raise error
    if len(tokens) > 1 and "(" not in tokens:
        raise CarlaeSyntaxError
    def parse_expression(index):
        """
        This function takes in an index as an input and parses a string expression, transforming it into a binary operation

        Input:
            index(int)
        Return:
            Binary Operation
        """
        right_side = []
        # if first element of the token is a closing parenthesis raise error
        if tokens[0] == ")" :
            raise CarlaeSyntaxError
        # if we are not at a parenthesis, return the token value
        if tokens[index] != "(" and tokens[index] != ")":
            return (number_or_symbol(tokens[index]), index + 1)
        elif tokens[index] == "(": # we know we are beginning a binary operation
            try:
                if tokens[index + 1] == ")":
                    return ([], index + 2)
                left_side, index = parse_expression(index + 1) # get the left side of binary operation
                left_side = [left_side]
                while tokens[index] != ")":
                    left_side2, index = parse_expression(index)# get left side of the binary operation
                    left_side += [left_side2]
                if tokens[index] == ")": # if we reach closing parenthesis, return expression
                    return (left_side, index + 1)
                else:
                    right_side, index = parse_expression(index) # get the right side of binary operation
                    right_side = [right_side]
            except:
                pass
        return (left_side + right_side , index + 1)         
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

  
def expression(text_expression):
    """
    This function returns a Binary Operation from a string expression

    Input:
        string of binary operation
    Return:
        Binary Operation
    """
    tokens = tokenize(text_expression)
    return parse(tokens)


######################
# Built-in Functions #
######################

def Sub(input):
    """
    This function return subtraction on its inputs
    """
    if len(input) == 1:
        return -input[0]
    else:
        return input[0] - sum(input[1:])

def Mul(input):
    """
    Thus function performs multiplication on the inputs
    """
    result = 0
    if len(input) == 2:
        return input[0] * input[1]
    else:
        result  += input[0] * Mul(input[1:])
    return result

def Div(input):
    """
    This function performs division on its inputs
    """
    if len(input) == 2:
        return input[0] / input[1]
    return input[0]/ Mul(input[1:])

def all_equal(args):
    """
    this function checks whether all of the args are equal to each other
    returns true or false
    """
    all_equal = True 
    first_elem = args[0]
    for arg in args:
        if arg != first_elem:
            all_equal = False
            break
    return all_equal

def greater_than(args):
    """
    this function checks whether or not each argument is each successive argument
    is greater than the last argument.
    Returns true or false
    """
    greater = True
    for i in range(len(args)-1):
        if args[i] <= args[i + 1]:
            greater = False
            break
    return greater

def greater_than_or_equall(args):
    """
    this function checks whether or not each argument is each successive argument
    is greater than or equall to the last argument.
    Returns true or false
    """
    greater = True
    for i in range(len(args) -1):
        if args[i] < args[i + 1]:
            greater = False
            break
    return greater

def less_than(args):
    """
    this function checks whether or not each argument is each successive argument
    is less than the last argument.
    Returns true or false
    """
    less = True
    for i in range(len(args)-1):
        if args[i] >= args[i + 1]:
            less = False
            break
    return less

def less_than_or_equall(args):
    """
    this function checks whether or not each argument is each successive argument
    is less than or equall to the last argument.
    Returns true or false
    """
    less = True
    for i in range(len(args) -1):
        if args[i] > args[i + 1]:
            less = False
            break
    return less

def not_func(arg):
    """
    This function returns the binary opposite of the input argument
    """
    if len(arg) != 1:
        raise CarlaeEvaluationError
    if arg[0]:
        return False
    return True

def pair(args):
    if len(args) != 2:
        raise CarlaeEvaluationError
    p = Pair(args[0], args[1])
    return p

def ret_head(arg):
    """
    this function returns the head of a pair
    """
    if len(arg) != 1 or not isinstance(arg[0], Pair):
        raise CarlaeEvaluationError
    return arg[0].head

def ret_tail(arg):
    """
    this function returns the tail of a head
    """
    if len(arg) != 1 or not isinstance(arg[0], Pair):
        raise CarlaeEvaluationError
    return arg[0].tail

def list_func(args):
    """
    this function creates a head a list with the pair structure
    """
    if args == []:
        return None
    else:
        head = args[0]
        return Pair(head, list_func(args[1:]))

def get_length(args):
    """
    This function returns the length of a pair object
    """
    if check_if_list(args):
        lst = args[0] 
        res = 0
        # if empty list lengh is zero
        if lst == None:
            return 0
        elif isinstance(lst, Pair):
            if lst != None:
                res += 1
            if lst.tail == None and lst.head:
                return 1
            # keep finding the tail untill tail is none
            while lst.tail != None:
                res += 1
                lst = lst.tail
            return res
    else:
        raise CarlaeEvaluationError

def check_if_list(object):
    """
    this function checks if the argument is a list
    """
    if isinstance(object, list):
        object = object[0]
    if isinstance(object, Pair): 
        if object.head or object.head == None or object.head == 0:
            # only a valid list if the tail is a pair and or the tail is none
            if isinstance(object.tail, Pair):
                return check_if_list(object.tail)
            elif object.tail == None:
                return True
            else:
                return False
    # if the object is an empty list
    elif object == None:
        return True
    else:
        return False

def return_item(args):
    """
    This returns the an item at an index from a list
    """
    if len(args) != 2:
        raise CarlaeEvaluationError
    lst = args[0]
    if lst == None:
        raise CarlaeEvaluationError
    index = args[1]
    assert index >= 0
    if isinstance(lst, Pair) and not check_if_list(lst):
        if index != 0:
            raise CarlaeEvaluationError
        return lst.head
    if index == 0:
        return lst.head
    else:
        return return_item([lst.tail, index-1])

def concatenate(args):
    """
    this function adds multiple lists together and returns the result list
    """
    for elem in args:
        if not check_if_list(elem):
            raise CarlaeEvaluationError
    # if only one list return a copy of that list
    if len(args) == 1:
        if args[0] == None:
            return None
        return Pair(args[0].head, args[0].tail)
    if len(args) == 0:
        return None
    # if an arg is none, then its an empty list
    if args[0] == None:
        return concatenate(args[1:])
    if args[0].tail == None:
        return Pair(args[0].head, concatenate(args[1:]))
    return Pair(args[0].head, concatenate([args[0].tail] + args[1:]))

def map(args):
    """
    this function maps a function to each element of the list
    """
    func = args[0]
    lst1 = args[1:]
    length = get_length(lst1)
    l = None
    for i in range(length):
        elem = return_item(lst1 + [i])
        res = func([elem])
        # use pointer structure to build the new list
        if i == 0:
            l = Pair(res, None)
            m = l
        else:
            m.tail = Pair(res, None)
            m = m.tail
    return l


def filter(args):
    """
    this function applies a filter to each element in a list.
    If the filter evaluates to true, add the filtered element to the new list
    """
    func = args[0]
    lst1 = args[1:]
    length = get_length(lst1)
    l = None
    m = None
    for i in range(length):
        elem = return_item(lst1 + [i])
        res = func([elem])
        if res:
            if l == None:
                l = Pair(elem, None)
                m = l
            else:
                m.tail = Pair(elem, None)
                m = m.tail
    return l

def reduce(args):
    """
    This function reduces the elements of a list and returns that value
    """
    func = args[0]
    lst = args[1:2]
    initval = args[2]
    length = get_length(lst)
    l = None
    for i in range(length):
        elem = return_item(lst + [i])
        res = func([initval, elem])
        initval = res
    return initval

def begin(args):
    return args[-1]









class builtins():
    def __init__(self):
        self.parent = None
        self.environment = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": Mul,
    "/": Div,
    "=?": all_equal,
    ">": greater_than,
    ">=": greater_than_or_equall,
    "<": less_than,
    "<=": less_than_or_equall,
    '@t': True,
    "@f": False,
    "not": not_func,
    "pair": pair,
    "head": ret_head,
    "tail": ret_tail,
    "nil": None,
    "list": list_func, 
    "list?": check_if_list,
    "nth": return_item,
    "length": get_length,
    "concat": concatenate,
    "map": map,
    "filter": filter,
    "reduce": reduce,
    "begin": begin
}

############
##CLASSES###
############

class Environment():
    """
    This class initializes environment and parent environment attributes to the environment object
    """
    #create instance variable of parent env
    def __init__(self, parent = None):
        self.environment = {}
        self.parent = parent

    def add_to_env(self, name, expression):
        self.environment[name] = expression


    def get_from_env(self, name):
        """
        This method returns the variables value if found in our environments
        """
        try:
            return self.environment[name]
        except KeyError:
            # keep trying to find the variable untill we reach the builtins, and then raise error
            while self.parent != None:
                self = self.parent
                if name in self.environment:
                    return self.environment[name]
            raise CarlaeNameError


class function():
    """
    This class initializes parameter, expression, and environment attributes to a function object
    """
    def __init__(self, parameters, func, env):
        self.parameters = parameters
        self.expression = func
        self.env = env

    def set_func_env(self, environment):
        self.env = environment

    def __call__(self, tree):
        environment = self.env
        new_env = Environment(environment)
        params = self.parameters
        arguments = tree
        if len(params) != len(arguments):
            raise CarlaeEvaluationError
        # map each arguments to each parameter
        for i,var in enumerate(params):
            new_env.add_to_env(var,arguments[i])
        return evaluate(self.expression, new_env, False) 

    


class Pair():
    """
    this class initializes ordered pairs.
    The attributes are head and tails
    """
    def __init__(self, head = None, tail = None):
        self.head = head
        self.tail = tail

    def __repr__(self):
        head = str(self.head)
        if self.tail == None:
            return head
        else:  
            return head +"," + repr(self.tail)
        

        


##############
# Evaluation #
##############



def evaluate(tree, environment = None, Start = True):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    if environment == None:
        environment = Environment(builtins())
    if isinstance(tree, list):
        
        remaining = []
        if len(tree) == 0:
            raise CarlaeEvaluationError
        if not isinstance(tree[0], list):
            # if we are defining variable
            if tree[0] == ":=":
                name = tree[1]
                # if we are performing a short function definition
                if isinstance(name, list):
                    parameters = name[1:]
                    name = name[0]
                    exp = tree[2]
                    # initialize function object
                    func = function(parameters, exp, environment)
                    environment.add_to_env(name, func)
                    return func
                val = tree[2]
                #otherwise, map the variable to its value as normal
                if not isinstance(val, list):
                    if val not in builtins().environment:
                         val = evaluate(tree[2], environment)
                else:
                    val = evaluate(val,environment)
                environment.add_to_env(name, val)
                return environment.get_from_env(name)
            # if we are defining a function
            elif tree[0] == "function":
                parameters = tree[1]
                exp = tree[2]
                func = function(parameters, exp, environment)
                return func
            # if we are entering an if statement
            elif tree[0] == "if":
                cond = evaluate(tree[1], environment)
                if cond == "@t" or cond == True:
                    return evaluate(tree[2], environment)
                elif cond == "@f" or cond == False:
                    return evaluate(tree[3], environment)
            # if we are entering an and statement
            elif tree[0] == "and":
                args = tree[1:]
                res = True
                for arg in args:
                    if evaluate(arg, environment) == False:
                        return False
                return True
            # if we are entering an or statement
            elif tree[0] == "or":
                args = tree[1:]
                res = False
                for arg in args:
                    if evaluate(arg, environment) == True:
                        return True
                return False
            # if we are deleting a variable 
            elif tree[0] == "del":
                var = tree[1]
                if var in environment.environment:
                    return environment.environment.pop(var)
                else:
                    raise CarlaeNameError
            # if we are creating a variable binding in a local environment
            elif tree[0] == "let":
                middle = tree[1]
                body = tree[2]
                new_env2 = Environment(environment)
                for comb in middle:
                    var1 = comb[0]
                    val = evaluate(comb[1], environment)
                    new_env2.add_to_env(var1, val)
                return evaluate(body, new_env2) 
            # if we are updating a variable binding 
            elif tree[0] == "set!":
                var = tree[1]
                expression = evaluate(tree[2], environment)
                perm_environment = environment
                while var not in perm_environment.environment: 
                    perm_environment = perm_environment.parent
                    if perm_environment.environment.keys() == builtins().environment.keys():
                        break
                if var in perm_environment.environment:
                    perm_environment.environment[var] = expression
                else:
                    raise CarlaeNameError
                return expression
            else:
                # if the first element of a list not a function, raise error
                if isinstance(tree[0], int):
                    raise CarlaeEvaluationError
                
                # if we are calling a valid function
                if isinstance(tree[0], function) or environment.get_from_env(tree[0]):
                    
                    # grab the function object

                    if isinstance(tree[0], function):
                        func1 = tree[0]   
                    else:
                        func1 = environment.get_from_env(tree[0])
                        while func1 in builtins().environment:
                            func1 = environment.get_from_env(func1)
                    for elem in tree[1:].copy():
                        remaining.append(evaluate(elem, environment))
                    return func1(remaining)
        else:
            #if the first element of tree is a list, we know this is a function
            res = evaluate(tree[0], environment)
            inp = [res]
            # evaluate each item in the rest of the tree
            for elem in tree[1:]:
                res1 = evaluate(elem, environment)
                inp.append(res1)
            # evaluate this function with the rest of the tree
            res = evaluate(inp, environment)
            return res
    
    else:
        if isinstance(tree, function):
            return tree
        else:
            # try and get variable name
            if type(tree) != int and type(tree) != float:
                if isinstance(tree, Pair):
                    return tree
                if tree == True or tree == False:
                    return tree
                if tree == None:
                    return None
                return environment.get_from_env(tree)
            else:
                return tree

def evaluate_file(filename, environment = None):
    if environment == None:
        environment = Environment(builtins())
    with open(filename) as f:
        read = f.read()
        arg = expression(read) 
        # print("arg", arg)
        return evaluate(arg, environment)

def result_and_env(tree, env = None):
    """
    perform evaluation, get the return environment, and then pass it into the next evaluate call
    """
    if env == None:
        env = Environment(builtins())
    result = evaluate(tree,env)
    return (result, env)


def repl(environment = None):
    """
    This function allows us to recreate a repl environment where the user can enter an input and have that be evaluated and printed
    """
    i = 0
    response = 0
    while response != "EXIT":
        try:
            # get the users expression
            response = input(">>>>")
            exp = expression(response)
            if i == 0:
                res = result_and_env(exp, environment)
                env = res[1]
                # print(res[0].tail.head)
                print(res[0])
                # print(res[0].head)
                i += 1
            else:
                res = result_and_env(exp, env)
                env = res[1]
                print(res[0])
                # print(res[0].head)
        except Exception as x:
            # if there was an error, print out statement and then ask the user for input again so that errors dont break our repl
            if response == "EXIT":
                break
            else:
                print(f"there was an error{x}")
                



# KEEP THE ABOVE LINES INTACT, BUT REPLACE THIS COMMENT WITH YOUR lab.py FROM
# THE PREVIOUS LAB, WHICH SHOULD BE THE STARTING POINT FOR THIS LAB.
if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    # args = sys.argv[1:]
    # environment = Environment(builtins())
    # for elem in args:
    #     res, environment = result_and_env(elem, environment)
    # repl(environment)
#     haha = result_and_env(expression("(:= foop 42)"))
#     haha2 = result_and_env(expression("""(:= myfunc (function (var100) ((function (var99) ((function (var98) ((function (var97) ((function (var96) ((function (var95) ((function (var94) ((function (var93) ((function (var92) ((function (var91) ((function (var90) ((function (var89) ((function (var88) ((function (var87) ((function (var86) ((function (var85) ((function (var84) ((function (var83) ((function (var82) ((function (var81) ((function (var80) ((function (var79) ((function (var78) ((function (var77) ((function (var76) ((function (var75) ((function (var74) ((function (var73) ((function (var72) ((function (var71) ((function (var70) ((function (var69) ((function (var68) ((function (var67) ((function (var66) ((function (var65) ((function (var64) ((function (var63) ((function (var62) ((function (var61) ((function (var60) ((function (var59) ((function (var58) ((function (var57) ((function (var56) 
# ((function (var55) ((function (var54) ((function (var53) ((function (var52) ((function 
# (foop) ((function (var50) ((function (var49) ((function (var48) ((function (var47) ((function (var46) ((function (var45) ((function (var44) ((function (var43) ((function (var42) ((function (var41) ((function (var40) ((function (var39) ((function (var38) ((function (var37) ((function (var36) ((function (var35) ((function (var34) ((function (var33) ((function (var32) ((function (var31) ((function (var30) ((function (var29) ((function (var28) ((function (var27) ((function (var26) ((function (var25) ((function (var24) ((function (var23) ((function (var22) ((function (var21) ((function (var20) ((function (var19) ((function (var18) ((function (var17) ((function (var16) ((function (var15) ((function (var14) ((function (var13) ((function (var12) ((function (var11) ((function (var10) ((function (var9) ((function (var8) ((function (var7) ((function (var6) ((function (var5) ((function (var4) ((function (var3) ((function (var2) ((function (var1) ((function (var0) (set! foop 30)) 0)) 1)) 2)) 3)) 4)) 5)) 6)) 7)) 8)) 9)) 10)) 11)) 12)) 13)) 14)) 15)) 16)) 17)) 18)) 19)) 20)) 21)) 22)) 23)) 24)) 25)) 26)) 27)) 28)) 29)) 30)) 31)) 32)) 33)) 34)) 35)) 36)) 37)) 38)) 39)) 40)) 41)) 42)) 43)) 44)) 45)) 46)) 47)) 48)) 49)) 50)) 51)) 52)) 53)) 54)) 55)) 56)) 57)) 58)) 59)) 60)) 61)) 62)) 63)) 64)) 65)) 66)) 67)) 68)) 69)) 70)) 71)) 72)) 73)) 74)) 75)) 76)) 77)) 78)) 79)) 80)) 81)) 82)) 83)) 
# 84)) 85)) 86)) 87)) 88)) 89)) 90)) 91)) 92)) 93)) 94)) 95)) 96)) 97)) 98)) 99)))"""), haha[1])
#     haha3 = result_and_env(expression("(myfunc 7)"), haha2[1])
    # haha = result_and_env(expression("(:= (contains? list_ elt) (if (=? nil list_) @f (if (=? (head list_) elt) @t (contains? (tail list_) elt))))"))
    # haha1 = result_and_env(expression("(if (contains? (list 1 2 3) 2) 1 0)"), haha[1])
#     
    repl()


    # repl()
    # haha = result_and_env(expression("(filter (function (x) (or (> x 0) (< x 0))) (list 1 1 1 1 0 0 0 -1 -1 -1 -1))"))
    # haha1 = result_and_env(expression("(list 1 1 1 1 0 0 0 -1 -1 -1 -1)"))
    # print(haha1[0].tail.tail.tail.tail.tail.tail.tail.tail.tail.tail.tail)
    # print(check_if_list(haha1[0]))
    # print(result_and_env(['begin', [':=', ['foo', 'bar'], ['function', ['x', 'y'], ['-', 'bar', 'x', 'y']]], [':=', 'bar', 7], [':=', 'something', ['foo', 6]], ['list', ['something', 2, 3], [['foo', 9], 8, 7]]])[0].head)
    # haha = result_and_env(expression("(:= x 7)"))
    # haha1 = result_and_env(expression("(:= y 8)"), haha[1])
    # haha2 = result_and_env(expression("(:= (square x) (* x x))"), haha1[1])
    # haha3 = result_and_env(expression("y"), haha2[1])
    # haha4 = result_and_env(expression("x"), haha3[1])
    # haha5 = result_and_env(expression("(square (del x))"), haha4[1])
    # haha1 = result_and_env(expression("(filter (function (x) (> x 0)) x)"), haha[1])

    # haha1 = result_and_env(expression("(:= x (list 7 9 3 2))"), haha[1])
    # haha2 = result_and_env(expression("(map factorial x)"), haha1[1])
    # haha2 = result_and_env(expression("(map factorial x)"), haha1[1])
    # haha3 = result_and_env(expression("x"), haha2[1])
    # haha4 = result_and_env(expression("(:= n 0)"), haha3[1])
    # haha5 = result_and_env(expression("(:= (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))"))
    
    # haha = result_and_env(expression("(:= (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))"))
    # haha1 = result_and_env(expression("(factorial 3)"), haha[1])
    # print(haha1[0])
    # haha1 = result_and_env(expression("(:= x (list 6 2 3 2))"), haha[1])
    # haha2 = result_and_env(expression("(map factorial x)  "), haha1[1])
    # haha = result_and_env(expression("(:= x (list 7 9 3 2))"))
    # haha1 = result_and_env(expression("(map - x)"), haha[1])
    # haha = check_if_list(haha[0])
    # print(haha)
    # haha = result_and_env(expression("(nth (list 1 2 3 4) 3)"))
    # print(haha[0])
    # print(result_and_env(expression("(=? nil nil)")))
    # repl()