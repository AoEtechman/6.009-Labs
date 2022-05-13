import doctest
import token


# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
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
        if var == self.name:
            return Num(1)
        else:
            return Num(0)

    def simplify(self):
        return self

    def eval(self, map):
        try:
            return map[self.name]
        except:
            return self




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
        return Num(0)

    def simplify(self):
        return self
    
    def eval(self, map):
        return self.n


class BinOp(Symbol):
    def __init__(self, left, right):
        if type(left) == int:
            self.left = Num(left)
        elif type(left) == str:
            try:
                int(left)
            except:
                self.left = Var(left)
        else:
            self.left = left
        if type(right) == int:
            self.right = Num(right)
        elif type(right) == str:
            try:
                int(right)
            except:
                self.right = Var(right)
        else:
            self.right = right    
      
    def __repr__(self):
        return self.name + "(" + repr(self.left) + "," + repr(self.right) + ')' 
    def __str__(self):
        left_string = str(self.left)
        right_string = str(self.right)
        if self.rank > self.left.rank:
            left_string = "(" + left_string + ')'
        if self.rank > self.right.rank:
            right_string = "(" + right_string + ")"
        if self.name == "Sub" or self.name == "Div":
            if self.rank == self.right.rank:
                right_string = "(" + right_string + ")"
        return left_string + self.op + right_string
    
    def eval(self, map):
        return self.eval(map)


    


class Add(BinOp):
    name = "Add"
    op = " + "
    rank = 0
    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)
    
    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n + right_simp.n)
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
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n - right_simp.n)
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
        return self.left * self.right.deriv(var)  + self.right * self.left.deriv(var)
    
    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n * right_simp.n)
        if isinstance(left_simp, Num):  
            if left_simp.n == 1:
                return right_simp
            elif left_simp.n == 0:
                return Num(0)
        if isinstance(right_simp, Num):  
            if right_simp.n == 1:
                return left_simp
            elif right_simp.n == 0:
                return Num(0)
        return Mul(left_simp, right_simp)

    def eval(self, map):
        return self.left.eval(map) * self.right.eval(map)

    


class Div(BinOp):
    name = "Div"
    op = " / "
    rank = 1
    def deriv(self, var):
        return (self.right * self.left.deriv(var)  - self.left * self.right.deriv(var))/(self.right * self.right)

    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        if isinstance(left_simp, Num) and isinstance(right_simp, Num):
            return Num(left_simp.n / right_simp.n)
        if isinstance(left_simp, Num):  
            if left_simp.n == 0:
                return Num(0)
        if isinstance(right_simp, Num):
            if right_simp.n == 1:
                return left_simp
        return Div(left_simp, right_simp)
    
    def eval(self, map):
        return self.left.eval(map) / self.right.eval(map)

def tokenize(str_input):
    token = []
    nums = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
    while len(str_input) != 0:
        if str_input[0] != " ":
            if str_input[0] in nums or (str_input[0] == "-" and str_input[1] in nums):
                ret = ""
                ret += str_input[0]
                str_input = str_input[1:]
                try:
                    while str_input[0] in nums:
                        ret += str_input[0]
                        print(ret)
                        str_input = str_input[1:]
                    token.append(ret)
                except:
                    token.append(ret)
                    break
            else:
                token.append(str_input[0])
                str_input = str_input[1:]
        else:
            str_input = str_input[1:]
    return token

def parse(tokens):
    def parse_expression(index):
        alphabet = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
        ops = {"+": "+", "-": "-", "*" : "*", "/": "/"}
        try:
            return (Num(int(tokens[index])), index + 1)
        except:
            if tokens[index] in alphabet:
                return (Var(tokens[index]), index + 1)
            else:
                if tokens[index] == "(":
                    left_side, operator_index = parse_expression(index + 1)
                    operator = tokens[operator_index]
                    right_side, index2 = parse_expression(operator_index + 1)
                    ops=["+","-","*","/"]
                    classes=[Add,Sub,Mul,Div]
                    return (classes[ops.index(ops[operator])](left_side, right_side), index2 + 1)
    print("expression", parse_expression(0))
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def expression(text_expression):
    tokens = tokenize(text_expression)
    return parse(tokens)





if __name__ == "__main__":
    doctest.testmod()
    # z = Add("x", Sub(Var('y'), Num(2)))
    # z = Mul(Var('x'), Add(Var('y'), Var('z')))
    # print(repr(z))
    # print(str(z))
    # print(repr(Var('x')))
    # print( repr(Num(3) + 'x'))
    # x = Var('x')
    # x + 2  # here, __add__ will be called
    # print(repr(Add(Var('x'), Num(2))))
    # # 2 + x  # here, __radd__ will be called
    # print(repr(Add(Num(2), Var('x'))))
#     x = Var('x')
#     y = Var('y')
#     # z = Mul(Add(Var('z'), Var('x')), 10)
#     # map = {'x': 3, 'z': 2}
#     # print(z.eval(map))
    # z = Add(Var('x'),  Num(0))

    # res = z.eval({'x': 877})
    # print(res/877 - 1)
    # print(expression("(5 + 6)"))

    # result = Sub(Var('k'), Num(5))
    # print(result.eval({'k': 583}))
    # print(result)
    print(tokenize(('(-101 * x)')))
    # print(repr(expression('(-101 * x)')))
