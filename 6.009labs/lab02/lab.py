# 6.009 Lab 2: Snekoban

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return level_description


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    
    computer_locations = list(find_computer_location(game)) #finds locations of computer
    win = False  # initializes win to false
    for location in computer_locations: # checks each computer location
        if "target" in game[location[0]][location[1]]: # if target is also in location, win is true
            win = True
        else:
            return False  # if a single location doesnt have a target and computer, game has not been won
    return win 



    

def find_player_location(game):
    """
    iterate through each location on the game board. 
    if player is found, return a tuple in the form (y,x)
    of the player's location.
    """
    for y in range(len(game)):
        for x in range(len(game[0])):
            if "player" in game[y][x]:
                return (y,x)

def find_computer_location(game):
    """
    This function takes in a game board input,
    finds the location of all of the computers on the board
    and returns a tuple of the computer locations.

    The function iterates through each location on the game board,
    if a computer is contained in that location, it appends the computer
    location list by that location. this list is then returned as a tuple.
    """
    
    computer_list = []
    for y in range(len(game)):
        for x in range(len(game[0])):
            if "computer" in game[y][x]:
                    computer_list.append((y,x))
    return tuple(computer_list)



def find_player_neighbors():
    """
    this function returns the directions up, down, right, and left
    to be used to find a specific locations neighbors. The function 
    takes no inputs
    """
    return ["left", "right", "up","down"]


def deep_copy_list(lst):
    """
    This function takes in a list input, and returns a deep copy of that list
    A deep copy of a list allows you to change the new copy without affecting the 
    original.

    The function checks if list is a list, then it iterates through all of the values in 
    lst and appends that to a new deep copied list. function is called recursively to account 
    for nested lists.
    """
    
    if type(lst) == list:
        return [deep_copy_list(value) for value in lst]
    return lst

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    new_game = deep_copy_list(game) # deep copy the game
    player_location = find_player_location(new_game) # find player location
    vector = direction_vector[direction] # get move vector
    output = []
    
    # get the ouput location of move vector being applied to the players location
    for i in range(len(vector)):
        output.append(vector[i]+player_location[i])
    output = tuple(output)
    
    # get the ouput location of a move vector being applied twice to the players location. 
    # this would allow is to move a computer when the player touches it
    output2 = []
    for i in range(len(vector)):
        output2.append(vector[i]+output[i])
    output2 = tuple(output2)
    
    # if we are not moving to a location with a wall
    if "wall" not in new_game[output[0]][output[1]]:
        
        # if we are moving to a space that is either empty or has a target, move the player to that space
        if new_game[output[0]][output[1]] == [] or "target" in new_game[output[0]][output[1]] and "computer" not in new_game[output[0]][output[1]]:
            new_game[player_location[0]][player_location[1]].remove("player")
            new_game[output[0]][output[1]].append("player")
            return new_game
        
        # if we try moving the player to a space with a computer and the computer can move, move the player 
        # and computer
        elif "computer" in new_game[output[0]][output[1]] and "wall" not in new_game[output2[0]][output2[1]] and "computer" not in new_game[output2[0]][output2[1]] :
            new_game[output[0]][output[1]].remove("computer")
            new_game[output2[0]][output2[1]].append("computer")
        
        # if we try to move the player to a space with a computer, but the computer cannot move,
        # do not perfor any moves
        elif "computer" in new_game[output[0]][output[1]] and "wall" in new_game[output2[0]][output2[1]] or "computer" in new_game[output2[0]][output2[1]]:
            return new_game        
        new_game[player_location[0]][player_location[1]].remove("player")
        new_game[output[0]][output[1]].append("player")
    return new_game



    


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    new_game = deep_copy_list(game) # deep copy game
    visited = set() # create set of visited states
    player_location = find_player_location(game)
    computer_locations = find_computer_location(game)
    
    # nodes are represented by game state, as well as player and computer locations at said game state
    agenda = [(new_game,(player_location, computer_locations))] 
    moves = [[]] # create list of moves

   
    while agenda: # while agenda is not empty
        state = agenda.pop(0) # pop from front
        move = moves.pop(0)
        if victory_check(state[0]): # if game state is a winning game, return moves
            return move
        else:
            if state[1] not in visited: # if state not visited, add it to visited
                visited.add(state[1])
                # print("visited", visited)
                # print("moves", move)
                neighbors = find_player_neighbors()
                new_game2 = deep_copy_list(state[0])
                
                # try moving to neighbor
                for neighbor in neighbors:
                    new_game3 = deep_copy_list(state[0])
                    new_game1 = step_game(new_game3, neighbor)   
                    if new_game1 != new_game2: # different games would mean that a valid move has been made
                        move1 = deep_copy_list(move)
                        move1.append(neighbor) # append each neighbor move to the current move
                        player_location = find_player_location(new_game1) # get new player and computer locations
                        computer_location = find_computer_location(new_game1)
                        agenda.append((new_game1,(player_location, computer_location))) #append agenda with new state
                        moves.append(move1) # append moves list with moves it took to get to the state that was most recently added to agenda
    return None # if we have gone through all possible moves and there is still no winner, return None

    



    


if __name__ == "__main__":
    # game = [
    #     [["computer"], ['wall'], ["target"]],
    #     [['player'], ['computer', "target"], ['target', "computer"]],
    # ]
    # if victory_check(game):
    #     print("True")
    # else:
    #     print("false")
#     game = [
#   [["wall"], ["wall"], ["wall"], ["wall"], [], []],
#   [["wall"], [], ["target"], ["wall"], [], []],
#   [["wall"], [], [], ["wall"], ["wall"], ["wall"]],
#   [["wall"], ["target", "computer"], ["player"], [], [], ["wall"]],
#   [["wall"], [], [], ["computer"], [], ["wall"]],
#   [["wall"], [], [], ["wall"], ["wall"], ["wall"]],
#   [["wall"], ["wall"], ["wall"], ["wall"], [], []]
# ]

    
#     print(solve_puzzle(game))
    pass
    
   
    
    

