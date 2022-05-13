#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    n = 2
    board = create_nd_array(n, [num_rows, num_cols], 0)
    visible = create_nd_array(n, [num_rows, num_cols], False)
    for bomb in bombs:
        change_val(board, list(bomb), n, ".")
    for loc in all_possible_coords([num_rows, num_cols],0):
        if get_val(board, loc, n) != ".":
            neighbors1 = create_neighbors(loc, n, n, (num_rows, num_cols))
            neighbor_bombs = 0
            for neighbor in neighbors1:
                if get_val(board, neighbor, n) == ".":
                    neighbor_bombs += 1
            change_val(board, loc, n, neighbor_bombs)
    return {"board": board,
    "dimensions": (num_rows, num_cols),
    "state": "ongoing",
    "visible": visible 
    }


    
def check_winNd(game):
    """
    Checks if a game has been won. Returns a boolean.

    Iterates through all of the locations on the board and check if all of the non bomb locations are visible.
    If this is the case, and there are zero covered squares, then return True. Else if there are more than zero 
    covered squares, return False.

    inputs:
        a game dictionary with dimensions, a board, a state, and a visited list. 

    returns:
        boolean indicating whether or not a game has been won
    """
    covered_squares = 0
    for loc in all_possible_coords(game["dimensions"], 0):
        if get_val(game["board"], list(loc), len(loc)) != ".":
            if not get_val(game['visible'], list(loc), len(loc)):
                covered_squares += 1
    if covered_squares == 0:
        return True
    else:
        return False

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
   
    n = 2
    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0
    if not get_val(game["visible"], [row, col], n):
        change_val(game["visible"], [row, col], n, True)
        revealed = 1
    else:
        return 0
    if get_val(game["board"], [row, col], n) == '.':
        game['state'] = 'defeat'
        return 1
    else:
        if get_val(game["board"], [row, col], n) != 0:
            revealed = 1
        else:
            neighbors1 = create_neighbors((row,col), 2,2, game["dimensions"])
            for neighbor in neighbors1:
                if not get_val(game["visible"], neighbor, n):
                    revealed += dig_nd(game, neighbor)
        if check_winNd(game):
            game['state'] = 'victory'
        return revealed



def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    dimensions = game['dimensions']
    new_game = create_nd_array(2, dimensions, 0)
    for loc in all_possible_coords(dimensions, 0):
        val = get_val(game['board'], loc, 2)
        if xray:   
            if val == 0:
                change_val(new_game, loc, 2, " ")
            else:
                change_val(new_game, loc, 2, f"{val}")
        else:
            if get_val(game['visible'], loc, 2):
                if val == 0:
                    change_val(new_game, loc, 2, " ")
                else:
                    change_val(new_game, loc, 2, f"{val}")
            else:
                change_val(new_game, loc, 2, "_")       
    return new_game
    

                         




def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    new_game = render_2d_locations(game, xray)  
    st = ""
    for i in range(len(new_game)):
        for elem in new_game[i]:
            st += elem
        if i < len(new_game) - 1:
            st += '\n'
    return st


# N-D IMPLEMENTATION
###HELPER FUNCTIONS

def create_nd_array(n, dimensions, value):
    """
    Creates a n dimensional array filled with input value

    Inputs:
        n: number of dimensions
        dimensions: dimensions
        value: value we want to input into array
    
    Returns:
        created n dimensional array
    """
    if n == 1:
        return [value]*dimensions[-1]
    else:
        return [create_nd_array(n-1, dimensions[1:], value) for i in range(dimensions[0])]

def change_val(board, loc, n, val):
    """
    changes value in n dimensional array at specified location

    Inputs:
        board: a game board
        loc: specified location
        n: number of dimensions
        val: value we want to place at specified location

    Returns:
        Nothing
    """
    if n == 1:
        board[loc[0]] = val
    else:
        return change_val(board[loc[0]], loc[1:], n-1, val)

def get_val(board, loc, n):
    """
    gets the value of the board at a specified location

    Inputs:
        board: a game board
        loc: a location on a board
        n: the number of dimensions

    returns:
        the value at the specified location
    """
    if n == 1:
        return board[loc[0]]
    else:
        return get_val(board[loc[0]], loc[1:], n-1)
    
    

def create_neighbors(loc, n, level, dimensions, neighbors = None):
    """
    creates a valid list of neighbor locations of a specified location on the board

    Inputs:
        loc: specified location
        n: number of dimensions
        level: current level of recursion
        dimensions: dimensions
        neighbors: current neighbors list

    returns:
        list of the locations valid neighbor locations.
    """
    if n == 1:
        return [[loc[0] + 1], [loc[0] - 1]]
    if level == n:
        lst = []
        for i in range(-1,2):
            if 0 <= loc[level-1] + i < dimensions[level-1]:
                lst.append([loc[level-1]+i])
        return create_neighbors(loc, n, level -1, dimensions, lst)
    elif level < n and level != 1:
        for neighbor in neighbors.copy():
            neighbor = neighbors.pop(0)
            for i in range(-1,2):
                copy = neighbor.copy()
                if 0 <= loc[level - 1] + i < dimensions[level -1]:
                    copy.insert(0, loc[level-1] + i)
                    neighbors.append(copy)
        return create_neighbors(loc, n, level-1, dimensions, neighbors)
    else:
        for neighbor in neighbors.copy():
            neighbor = neighbors.pop(0)
            for i in range(-1,2):
                copy = neighbor.copy()
                if 0 <= loc[level - 1] + i < dimensions[level -1]:
                    copy.insert(0,loc[level-1] + i)
                    neighbors.append((copy))
        neighbors.remove(list(loc))
        neighbors = neighbors.copy()
        return neighbors

def all_possible_coords(dimensions, level, coordinates = None):
    """
    creates a list of all of the possible locations on a given game board

    Inputs:
        dimensions: the dimensions of the game
        level: The current level of the recursion
        coordinates: a list of all of the current coordinates in the game board

    Returns:
        A list of all of the coordinates in a game board
    """
    if level == len(dimensions):
        return coordinates
    else:  
        if level == 0:
            coordinates = []
            for i in range(dimensions[level]):
                coordinates.append([i])
            all_possible_coords(dimensions, level + 1, coordinates) 
        else:
            for coord in coordinates.copy():
                for i in range(dimensions[level]):
                    coordinates.append(coord + [i])
                coordinates.remove(coord)
            level += 1
            all_possible_coords(dimensions, level, coordinates) 
    return coordinates


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    
    n = len(dimensions)
    board = create_nd_array(n, dimensions, 0)
    visible = create_nd_array(n, dimensions, False)
    for bomb in bombs:
        change_val(board, list(bomb), n, ".")
    for loc in all_possible_coords(dimensions,0):
        if get_val(board, loc, n) != ".":
            neighbors1 = create_neighbors(loc, n, n, dimensions)
            neighbor_bombs = 0
            for neighbor in neighbors1:
                if get_val(board, neighbor, n) == ".":
                    neighbor_bombs += 1
            change_val(board, loc, n, neighbor_bombs)
    return {"board": board,
    "dimensions": dimensions,
    "state": "ongoing",
    "visible": visible 
    }


def dig_nd(game, coordinates, should_check = True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    n = len(coordinates)
    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0
    if not get_val(game["visible"], list(coordinates), n):
        change_val(game["visible"], list(coordinates), n, True)
        revealed = 1
    else:
        return 0
    if get_val(game["board"], list(coordinates), n) == '.':
        game['state'] = 'defeat'
        return 1
    elif get_val(game["board"], list(coordinates), n) == 0:
            neighbors1 = create_neighbors(coordinates, n, n, game["dimensions"])
            for neighbor in neighbors1:
                if not get_val(game["visible"], neighbor, n):
                    revealed += dig_nd(game, neighbor, False)
    if should_check:
        if check_winNd(game):
            game["state"] = "victory"
    return revealed





def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    dimensions = game['dimensions']
    n = len(dimensions)
    new_game = create_nd_array(n, dimensions, 0)
    for loc in all_possible_coords(dimensions, 0):
        val = get_val(game['board'], loc, n)
        if xray:   
            if val == 0:
                change_val(new_game, loc, n, " ")
            else:
                change_val(new_game, loc, n, f"{val}")
        else:
            if get_val(game['visible'], loc, n):
                if val == 0:
                    change_val(new_game, loc, n, " ")
                else:
                    change_val(new_game, loc, n, f"{val}")
            else:
                change_val(new_game, loc, n, "_")       
    return new_game
    


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    pass


    



