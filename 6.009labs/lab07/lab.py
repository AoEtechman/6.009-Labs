import doctest



# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    # overwrite all dunder methods so that we can user operators to perform Binary operations.
    # Ex: we can use Var('x') * Num(2) to represent Mul(Var('x), Num(2))
    def __add__(self, second):
        return Add(self, second)
    def __sub__(self, second):
        return Sub(self, second)
    def __mul__(self, second):
        return Mul(self, second)
    def __truediv__(self, second):
        return Div(self, second)
    def __radd__(self, second):
        return Add(self, second)
    def __rsub__(self, second):
        return Sub(second, self)
    def __rmul__(self, second):
        return Mul(self, second)
    def __rtruediv__(self, second):
        return Div(second, self)
    def __rpow__(self, second):
        return Pow(second, self)
    def __pow__(self, second):
        return Pow(self, second)



class Var(Symbol):
    rank = 3
    def __init__(self, name):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"

    def deriv(self, var):
        if var == self.name: # if taking derivative of variable with respect to itself
            return Num(1)
        else:
            return Num(0)

    def simplify(self):
        return self

    def eval(self, map):
        try: # try to retrieve map value
            return map[self.name]
        except:
            raise KeyError(" No such variable in equation")




class Num(Symbol):
    rank = 3
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"

    def deriv(self, var):
        return Num(0) # derivative of const is zero

    def simplify(self):
        return self
    
    def eval(self, map):
        return self.n # return the actual number value 


class BinOp(Symbol):
    # initialize inputs to BinOp
    def __init__(self, left, right):
        """
        Initializer.  Store two instance variables called 'left' and 'right', containing the
        values passed in to the initializer.
        """
        
        if type(left) == int:
            self.left = Num(left)
        elif type(left) == str:
            try: # make sure that variable in the string is not a number
                int(left)
            except:
                self.left = Var(left)
        else:
            self.left = left
        if type(right) == int:
            self.right = Num(right)
        elif type(right) == str:
            try: # make sure variable in the string is not a number
                int(right)
            except: 
                self.right = Var(right)
        else:
            self.right = right    
      
    def __repr__(self):
        """
        prints representation of Binary Operation
        """
        return self.name + "(" + repr(self.left) + "," + repr(self.right) + ')' 
    def __str__(self):
        """
        This function returns the string representation of a Binary Operation
        """
        left_string = str(self.left)
        right_string = str(self.right)
        if self.rank >= 2: 
            if self.rank >= self.left.rank:
                left_string = "(" + left_string + ')'
        elif self.rank > self.left.rank: # if the left side of Binary operation has less precedence in PEMDAS than the main operator, enclose the left side in parentheses
            left_string = "(" + left_string + ')'
        if self.rank > self.right.rank: # if the right side of Binary operation has less precedence in PEMDAS than the main operator, enclose the right side in parentheses
            right_string = "(" + right_string + ")"
        if self.name == "Sub" or self.name == "Div": 
            if self.rank == self.right.rank: # if the right side of Binary operation has the same precedence in PEMDAS as the main operator then enclose the right side in parentheses
                right_string = "(" + right_string + ")"
        return left_string + self.op + right_string # return string representation of Binary Operation


    


class Add(BinOp):
    name = "Add"
    op = " + "
    rank = 0
    def deriv(self, var):
        """
        This function performs a derivative on a Binary Operation
        """
        return self.left.deriv(var) + self.right.deriv(var)
    
    def simplify(self):
        """
        This function performs a derivative on a Binary Operation
        """
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n + right_simp.n)
        # if adding zero to a number, simplify to that number
        if isinstance(left_simp, Num): 
            if left_simp.n == 0:
                return right_simp
        if isinstance(right_simp, Num):
            if right_simp.n == 0:
                return left_simp
        return Add(left_simp, right_simp)
    
    def eval(self, map):
        return self.left.eval(map) + self.right.eval(map)
        




class Sub(BinOp):
    name = "Sub"
    op = " - "
    rank = 0
    def deriv(self, var):
        """
        This function performs a derivative on a Binary Operation
        """
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        """
        This function performs a derivative on a Binary Operation
        """
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n - right_simp.n)
        # if subtracting a number by 0, simplify to that number
        if isinstance(right_simp, Num):
            if right_simp.n == 0:
                return left_simp
        return Sub(left_simp, right_simp)

    def eval(self, map):
        return self.left.eval(map) - self.right.eval(map)

    

class Mul(BinOp):
    name = "Mul"
    op = " * "
    rank = 1
    def deriv(self, var):
        """
        This function performs a derivative on a Binary Operation
        """
        return self.left * self.right.deriv(var)  + self.right * self.left.deriv(var)
    
    def simplify(self):
        """
        This function performs a derivative on a Binary Operation
        """
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n * right_simp.n)
        if isinstance(left_simp, Num):  
            if left_simp.n == 1: # if multiplying number by 1, simplify to number
                return right_simp
            elif left_simp.n == 0: # if multiplying a number by 0 simplify to zero
                return Num(0)
        if isinstance(right_simp, Num):  # if multiplying number by 1, simplify to number
            if right_simp.n == 1:
                return left_simp
            elif right_simp.n == 0: # if multiplying a number by 0 simplify to zero
                return Num(0)
        return Mul(left_simp, right_simp)

    def eval(self, map):
        return self.left.eval(map) * self.right.eval(map)

    


class Div(BinOp):
    name = "Div"
    op = " / "
    rank = 1
    def deriv(self, var):
        """
        This function performs a derivative on a Binary Operation
        """
        return (self.right * self.left.deriv(var)  - self.left * self.right.deriv(var))/(self.right * self.right)

    def simplify(self):
        """
        This function simplifies a Binary Operation
        """
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n / right_simp.n)
        if isinstance(left_simp, Num):  # if dividing a zero by a number, simplify to 1
            if left_simp.n == 0:
                return Num(0)
        if isinstance(right_simp, Num): # if diving a number by 1, simplify to that number
            if right_simp.n == 1:
                return left_simp
        return Div(left_simp, right_simp)
    
    def eval(self, map):
        return self.left.eval(map) / self.right.eval(map)


class Pow(BinOp):
    rank = 2
    name = "Pow"
    op = " ** "
    def deriv(self, var):
        """
        This function performs a derivative on a Binary Operation
        """
        if isinstance(self.right, Num):
            return (self.left**(self.right - Num(1)) * self.right ) * self.left.deriv(var)
        else:
            raise TypeError("We cann only perform derivates on a value being raised by a number power")

    def simplify(self):
        """
        This function simplifies a Binary Operation
        """
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(right_simp, Num) and isinstance(left_simp, Num):
            return Num(left_simp.n ** right_simp.n)
        if isinstance(right_simp, Num): 
            if right_simp.n == 0: # if raising a number to power 0, simplify to 1
                return Num(1)
            elif right_simp.n == 1: # if raising a number to power 1, simplify to number
                return left_simp
        if isinstance(left_simp, Num): # if raising zero to power n, for n in all real numbers and variables, simplify to zero
            if left_simp.n == 0:
                return Num(0)
        return Pow(left_simp, right_simp)

    def eval(self, map):
        return self.left.eval(map) ** self.right.eval(map)
    

def tokenize(str_input):
    """
    This fucntion takes a string expression and splits it up into its individual pieces

    Input:
        a string input
    Returns:
        a list of all of the pieces in the expression
    """
    token = []
    nums = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
    while len(str_input) != 0:
        if str_input[0] != " ":
            if str_input[0] in nums or (str_input[0] == "-" and str_input[1] in nums): # get numbers from expression
                ret = ""
                ret += str_input[0]
                str_input = str_input[1:]
                try: # keep iterating through the expression untill we reach a non number character or we reach the end of the expression
                    while str_input[0] in nums:
                        ret += str_input[0]
                        str_input = str_input[1:]
                    token.append(ret)
                except:
                    token.append(ret)
                    break
            else:
                if str_input[0] == "*": # check for multiplication or power characters in expression
                    if str_input[1] == "*":
                        token.append("**")
                        str_input = str_input[2:]
                    else:
                        token.append(str_input[0])
                        str_input = str_input[1:]
                else: # if it is any character that is not a number, add it to the return list
                    token.append(str_input[0])
                    str_input = str_input[1:]
        else: # if it is a space do not add to return list
            str_input = str_input[1:]
    return token

def parse(tokens):
    """
    This function returns a Binary Operation from a string expression

    Input:
        string of binary operation
    Return:
        Binary Operation
    """
    print(tokens)
    def parse_expression(index):
        """
        This function takes in an index as an input and parses a string expression, transforming it into a binary operation

        Input:
            index(int)
        Return:
            Binary Operation
        """
        alphabet = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
        ops = {"+": 0, "-": 1, "*" : 2, "/": 3, "**": 4}
        try: # checks if item in token is an int, if so, turn it into a number object and return it with index + 1
            return (Num(int(tokens[index])), index + 1)
        except:
            if tokens[index].lower() in alphabet: # if item in token is a character, turn it into a variable object and return it with index + 1
                return (Var(tokens[index]), index + 1)
            else:
                if tokens[index] == "(": # we know we are beginning a binary operation
                    left_side, operator_index = parse_expression(index + 1) # get the left side of binary operation
                    operator = tokens[operator_index] # get the operator
                    right_side, index2 = parse_expression(operator_index + 1) # get the right side of binary operation
                    classes=[Add,Sub,Mul,Div,Pow]
                    return (classes[ops[operator]](left_side, right_side), index2 + 1) # return the binary operation
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





if __name__ == "__main__":
    doctest.testmod()