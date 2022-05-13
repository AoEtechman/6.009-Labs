#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest


# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


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

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": Mul,
    "/": Div,
}

class builtins():
    def __init__(self):
        self.parent = None
        self.environment = {
    "+": sum,
    "-": Sub,
    "*": Mul,
    "/": Div,
}

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
    This function initializes parameter, expression, and environment attributes to a function object
    """
    def __init__(self, parameters, func, env):
        self.parameters = parameters
        self.expression = func
        self.env = env

    def set_func_env(self, environment):
        self.env = environment

    def __call__(self, tree, environment):
        new_env = Environment(environment)
        params = self.parameters
        args = tree[1:]
        arguments = []
        for elem in args:
            arguments.append(evaluate(elem, environment, False))
        if len(params) != len(arguments):
            raise CarlaeEvaluationError
        # map each arguments to each parameter
        for i,var in enumerate(params):
            new_env.add_to_env(var,arguments[i])
        return evaluate(self.expression, new_env, False)  



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
            elif tree[0] == "if":
                cond = evaluate(tree[1], environment)
                if cond == "@t" or cond == True:
                    return evaluate(tree[2], environment)
                elif cond == "@f" or cond == False:
                    return evaluate(tree[3], environment)
            elif tree[0] == "and":
                args = tree[1:]
                res = True
                for arg in args:
                    if evaluate(arg, environment) == False:
                        return False
                return True
            elif tree[0] == "or":
                args = tree[1:]
                res = False
                for arg in args:
                    if evaluate(arg, environment) == True:
                        return True
                return False
            
            else:
                # if the first element of a list not a function, raise error
                if isinstance(tree[0], int):
                    raise CarlaeEvaluationError
                
                # if we are calling a valid function
                if isinstance(tree[0], function) or environment.get_from_env(tree[0]):
                    
                    # grab the function object

                    if isinstance(tree[0], function):
                        func1 = tree[0]   
                        environment = func1.env
                    else:
                        func1 = environment.get_from_env(tree[0])
                        if func1 in builtins().environment:
                            func1 = environment.get_from_env(func1)
                    try:
                        for elem in tree[1:].copy():
                            remaining.append(evaluate(elem, environment, False))
                        return func1(remaining, environment)
                    except TypeError:
                        if Start:
                            environment = func1.env
                        return func1(tree, environment)
                    
        else:
            result = 0
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
        if tree in carlae_builtins:
            return carlae_builtins[tree]
        else:
            # try and get variable name
            if type(tree) != int and type(tree) != float:
                return environment.get_from_env(tree)
            else:
                return tree

def result_and_env(tree, env = None):
    """
    perform evaluation, get the return environment, and then pass it into the next evaluate call
    """
    if env == None:
        env = Environment(builtins())
    result = evaluate(tree,env)
    return (result, env)


def repl():
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
                res = result_and_env(exp)
                env = res[1]
                print(res[0])
                i += 1
            else:
                res = result_and_env(exp, env)
                print(res[0])
                env = res[1]
        except:
            # if there was an error, print out statement and then ask the user for input again so that errors dont break our repl
            print("there was an error")
    response = input(">>>>")


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    # repl()
#     haha1 = result_and_env([
#     ":=",
#     "addN",
#     [
#       "function",
#       [
#         "n"
#       ],
#       [
#         "function",
#         [
#           "i"
#         ],
#         [
#           "+",
#           "i",
#           "n"
#         ]
#       ]
#     ]
#   ])
#     print(haha1[0].expression)
#     haha = result_and_env([
#     ":=",
#     "add7",
#     [
#       "addN",
#       7
#     ]
#   ], haha1[1])
#     haha2 = result_and_env([
#     "add7",
#     2
#   ], haha[1])
#     print(haha2[0])
#     print(haha[1].environment)
#     print(haha[0].expression)
#     print(haha[0].parameters)
    # if n == 1:
    #     return n
    # else:
    #     return n*factorial(n-1)
    haha = result_and_env(expression("(:= (spam) (* eggs 3))"))
    haha1 = result_and_env(expression("(spam)"), haha[1])
    # haha2 = result_and_env(expression("(:= eggs 20)"), haha1[1])
