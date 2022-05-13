"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
TEXT = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
GRAPHICAL = {"snek", 'flag', 'rock', 'wall', 'computer', 'bug'}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = TEXT | PROPERTIES | {"AND", "IS"}
WORDS2 = {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def deep_copy_list(lst):
    """
    This function returns a deep copy of a list
    """
    if isinstance(lst, list):
        return [deep_copy_list(elem) for elem in lst]
    return lst
    
def find_rules(board, location):
    """
    This function takes a text string, finds the rest of the elements in the strings row and column,
    parses the rules, and returns a dictionary mapping each text string to its property

    Inputs:
            board: a nested list representing a board
            location: the location of the text string
    """
    
    cur_y, cur_x = location
    rules_1 = board[cur_y][cur_x:] # find the rest of the rules row
    rules_2 = [ row[cur_x] for ix, row in enumerate(board) if ix >= cur_y] # find the rest of the elements in the rules column
    rules_1_dict = parse_rules(rules_1)
    rules_2_dict = parse_rules(rules_2)
    
    # return a combined dictionary 
    for subject in rules_2_dict:
        if subject not in rules_1_dict:
            rules_1_dict[subject] = rules_2_dict[subject]
        else:
            for prop in rules_2_dict[subject]:
                rules_1_dict[subject].add(prop)
    return rules_1_dict


def parse_rules(rules_list):
    """
    This function takins in a list of rules lists, and creates the mapppings between subjects and their properties

    Inputs:
            a list of lists
    output:
            a dictionary subject property mappings
    """
    subject_dict = {}
    if rules_list[0]: # get the subject
        subject_dict[rules_list.pop(0)[0]] = set()
    res = {}
    properties = []
    while rules_list:
        try:
            # try and get all of the subjects in the rules list
            while rules_list[0][0] == "AND":
                if rules_list[1][0] in TEXT:
                    subject_dict[rules_list[1][0]] = set()
                    rules_list = rules_list[2:]
                else:
                    break
        except IndexError:
            return {}
        # get all of the properties for the subjects
        if rules_list[0] and rules_list[0][0] == "IS":
            if rules_list and len(rules_list) >= 2 and rules_list[1] and rules_list[1][0] in TEXT | PROPERTIES: # if we found a property
                properties.append(rules_list[1][0])
                rules_list = rules_list[2:]
                while rules_list and rules_list[0] and rules_list[0][0] == "AND": # try and get the rest of the properties if there are multiple
                    if rules_list[1] and rules_list[1][0] in TEXT | PROPERTIES:
                        if len(rules_list) >= 3:
                            if rules_list[2] and rules_list[2][0] == "IS": #we are creating a new rule
                                res = parse_rules(rules_list[1:])
                                rules_list = []
                            else:
                                properties.append(rules_list[1][0]) # add the properties we have found
                                rules_list = rules_list[2:]

                        elif len(rules_list) >= 2:
                            properties.append(rules_list[1][0]) # add the properties we have found
                            rules_list = rules_list[2:]
                break
            else:
                return {}
        else:
            return {}
    
    # return a combined dictionary of all of the rule mappings
    for elem in subject_dict:
        subject_dict[elem] = set(properties)
    for subject in res:
        if subject not in subject_dict:
            subject_dict[subject] = res[subject]
        else:
            for prop in res[subject]:
                subject_dict[subject].add(prop)
    return subject_dict


def set_object_properties(rule_mappings):
    """
    this function updates the graphical object instances properties using the property mapping dictionary

    Input:
        a dictionary of rule_mappings
    Returns:
            returns None
    """
    for subject, property in rule_mappings.items():
        subject = subject.lower()
        for graph_object in Graphical_object.objects:
            if graph_object.value == subject and property:
                graph_object.set_property(property) # set the property of the object instance
    



class Game:
    """
    The game object class initializes the game and sets the game rules. It also contains all of the functions
    that operate on the game, including move, update_board, chain_moves, valid_move, check_win, check_defeat, transform_objects
    Attributes:
            instance attribute board: the nested list game board
            instance attribute rows: number of board rows
            instance attribute cols: number of board cols
            class attribute rules: the rules mapping dictionary
    """
    def __init__(self, orig_board):
        Graphical_object.objects = []
        rule_mappings = []
        board = deep_copy_list(orig_board)
        for ix,row in enumerate(board):
            for ix2, col in enumerate(row):
                location = (ix, ix2)
                loc = board[ix][ix2]
                if loc != []:
                    for val in loc.copy():
                        if val in GRAPHICAL:
                            loc.remove(val)
                            loc.append(Graphical_object(val,set(), location))
                        elif val in TEXT:
                            rule_mappings.append(find_rules(board, location))
        for rule in rule_mappings:
            set_object_properties(rule)
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        Game.rules = rule_mappings
        
    def move(self, direction):
        """
        This function takes a direction and carries out all of the movements that are a result of that direction

        Input:
            direction
        Outputs:
            None
        """
        direction = direction_vector[direction]
        for object in Graphical_object.objects:
            if "YOU" in object.property:
                if self.valid_move(self.rows, self.cols, direction, object.location):# check if we can perform this move
                    new_loc = (direction[0] + object.location[0], direction[1] + object.location[1])
                    for obj in self.board[object.location[0]][object.location[1]]:
                        if "YOU" in obj.property: 
                            self.board[object.location[0]][object.location[1]].remove(obj)# remove the object from current location
                    object.location = new_loc
                    self.chain_moves(direction, new_loc, True)# chain all of the moves that are a result of the object moving
                    self.board[object.location[0]][object.location[1]].append(object)# add the object to its new location
        
        # rebuild the game
        Graphical_object.objects = [] 
        self = Game(dump_game(self))
    
    def update_board(self):
        """
        This function updates the board rules, object properties, etc based on the last move

        Inputs:
            None
        Outputs:
            None
        """
        
        self.transform_objects() # if any objects have the property of another object, change those objects to their property
        for row in self.board:
            for col in row:
                for elem in col:
                    if isinstance(elem, Graphical_object):
                        # reset the element
                        elem.property = set()
                        elem.has_moved = False 
                        for obj in Graphical_object.objects:
                            if elem.value == obj.value:
                                elem.set_property(obj.property) # set the objects property to the new updated property
                                if not elem.property:# if the object has no properties currently, check to see if we have new properties that we can update it with
                                    for rule in self.rules:
                                        for name in rule:
                                            if name.lower() == elem.value:
                                                elem.set_property(rule[name]) # set the object properties to be the updated properties if the object currently
                                                # has no property

        
    def chain_moves(self, direction, new_loc, pull = True,):
        """
        This function chains all the moves that are a result of the moving the you objects

        Inputs:
            direction: the direction vector
            new_loc: the location where the you object moved into
            pull: a boolean determining if we should check for pull objects\

        Outputs:
            None
        """
        if pull:# check to see if there is an object that we can pull
            backwards_y, backwards_x = direction[0] * -2 + new_loc[0], direction[1] * -2 + new_loc[1] # the location behind where the you object was
            if self.valid_move(self.rows, self.cols, direction, (backwards_y, backwards_x)): 
                try:
                    if backwards_y == -1 or backwards_x == -1: # the object is on the opposite side of the board and not actually behind the you object
                        raise IndexError
                    for val in self.board[backwards_y][backwards_x].copy():
                        if isinstance(val, Graphical_object) and "PULL" in val.property and val.has_moved == False: # if it is an object we can pull and it has not moved, pull the object
                            self.board[backwards_y][backwards_x].remove(val)
                            val.moved()
                            new_back_loc = backwards_y + direction[0], backwards_x + direction[1]
                            val.location = (new_back_loc[0], new_back_loc[1])
                            self.board[new_back_loc[0]][new_back_loc[1]].append(val)
                            self.chain_moves(direction, new_back_loc, True)# see if there are other pull moves that we can chain
                except IndexError:
                    pass
        try:
            for val in self.board[new_loc[0]][new_loc[1]]: # this is for chaining push objects
                if val in WORDS or isinstance(val, Graphical_object) and "PUSH" in val.property and val.has_moved == False:# if it is a push object that we can chain and it has not been moved yet
                    next_y, next_x = new_loc[0] + direction[0], new_loc[1] + direction[1]
                    if isinstance(val, Graphical_object):
                        next_backwards = (next_y + direction[0] * -2, next_x + direction[1] * -2)
                        self.board[new_loc[0]][new_loc[1]].remove(val)
                        # check if pushing this object caused a pull object to move
                        for val2 in self.board[next_backwards[0]][next_backwards[1]].copy():
                            if "PULL" in val2.property:
                                self.chain_moves(direction, (next_y, next_x), True)
                        val.moved()
                        val.location = (next_y, next_x)
                        self.chain_moves(direction, (next_y, next_x), False)# chain the moves that are a result of pushing that object
                        self.board[val.location[0]][val.location[1]].append(val)
                    else:
                        self.board[new_loc[0]][new_loc[1]].remove(val)
                        self.chain_moves(direction, (next_y, next_x), False)
                        self.board[next_y][next_x].append(val)
            
        except IndexError:
            pass
            

    def valid_move(self, rows, cols, direction, location):
        """
        this function checks if all of the moves that are a result of moving the you objects are valid moves.
        if True, we perform the moves, if false, we perform none of the moves

        Inputs:
            rows: number of board rows
            cols: number of board cols
            direction: a direction vector
            location: current coordinates of the you object
        Outputs:
            boolean
        """
        # get the location we want to move into
        new_y = direction[0] + location[0]
        new_x = direction[1] + location[1]
        if 0 <= new_y < rows:
            if 0 <= new_x < cols:# if within the board boundaries
                res = True
                for ix, val in enumerate(self.board[new_y][new_x].copy()):
                    # for all of the objects that can be chained, check if they can validly move, if so, return true, otherwise return false
                    if isinstance(val, Graphical_object) or val in WORDS:
                        if val in WORDS or "PUSH" in val.property:
                                res = self.valid_move(rows, cols, direction, (new_y, new_x))
                                if res == False:# if we get one false move, we know that chaining moves wont work
                                    return res
                        elif isinstance(val, Graphical_object) and "STOP" in val.property:
                            return False
                return res
        return False

    def check_defeat(self):
        """
        This function removes objects that are on defeat squares or have the defeat property

        Inputs:
            None
        Outputs:
            None
        """
        objects = Graphical_object.objects
        for object in objects.copy():
            if "DEFEAT" in object.property:
                if "YOU" in object.property:# if a graphical object has the property of defeat and you, remove all instances of that object
                    for object1 in self.board[object.location[0]][object.location[1]]:
                        if "YOU" in object1.property:
                            self.board[object.location[0]][object.location[1]].remove(object1)
                            Graphical_object.objects.remove(object)
                            try:
                                Graphical_object.objects.remove(object1)
                            except:
                                pass
                else:# else check all objects and see if they are on the same square as another object with the defeat property
                    for object2 in objects.copy():
                        if object2.location == object.location and "YOU" in object2.property:# if they are on the same square
                            for object3 in self.board[object2.location[0]][object2.location[1]]:
                                if isinstance(object3, Graphical_object) and "YOU" in object3.property:
                                    self.board[object2.location[0]][object2.location[1]].remove(object3)# remove the object
                                    Graphical_object.objects.remove(object2)

    def check_win(self):
        """
        This function checks whether or not we have won the game. This happens when a you object is on the same square as
        anther object with the property you, or the you object also has the property win.

        Inputs:
            None
        Outputs:
            boolean
        """
        objects = Graphical_object.objects
        for object in objects:
            if "WIN" in object.property:
                if "YOU" in object.property:# if object has property you and win, we have won the game
                    return True
                for object2 in objects:
                    if "YOU" in object2.property:
                        # if we have 1 object with you property in the same location as an object with the win property
                        # we have won
                        if object2.location == object.location:
                            return True
        return False

    def transform_objects(self):
        """
        This function checks if any objects have another graphical object as its property, and changes the object to its property representaion

        Inputs:
            None
        Ouputs:
            None
        """
        for object in Graphical_object.objects.copy():
            for property in object.property.copy():
                if property in TEXT: # if object has another graphical object as property
                    object.property.remove(property)
                    property = property.lower()
                    new_obj = Graphical_object(property,object.property, object.location)# create new object with all of the original objects properties except for the graphical object property
                    y, x = object.location[0], object.location[1]
                    for elem in self.board[y][x].copy():
                        if isinstance(elem, Graphical_object) and elem.value == object.value:
                            self.board[y][x].remove(elem)
                            self.board[y][x].append(new_obj)# add the new object
                            Graphical_object.objects.remove(object)# remove the old object from list of graphical objects
                    

class Graphical_object(Game):
    """
    This class initializes graphical game objects.
    Instance Attributes:
        value: the value or name of object
        property: a set of properties that the object has
        location: the objects location
        has_moved = a boolean determining whether the object has moved within a turn
    Class Attributes:
        objects: a list of all graphical object instances
    """
    objects = []
    def __init__(self, value, property, location):
        self.value = value
        self.property = property
        self.location = location
        self.has_moved = False
        Graphical_object.objects.append(self)

    def set_property(self, property):
        """
        This function adds properties to an object's property set
        """
        self.property |= property
    
    def moved(self):
        """
        this function updates objects move status
        """
        self.has_moved = True





        
def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return Game(level_description)


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    game.move(direction)
    game.update_board()
    game.check_defeat()
    return game.check_win()



def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    board = deep_copy_list(game.board)
    for ix, row in enumerate(board):
        for ix2, col in enumerate(row):
            for val in col.copy():
                if isinstance(val, Graphical_object):
                    board[ix][ix2].remove(val)
                    board[ix][ix2].append(val.value)
    return board





if __name__ == "__main__":
    pass