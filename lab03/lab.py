#!/usr/bin/env python3


import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}

def deep_copy_list(lst):
    """
    This function takes in a list input and returns a deep copy of the list
    """
    if isinstance(lst, list):
        return [deep_copy_list(elem) for elem in lst]
    return lst

def build_internal_representation(nodes_filename, ways_filename):
    """
    this function takes in an input of a nodes file and a ways file.

    the function processes the data and returns two dictionaries in tuple format.
    The first dictionary contains keys of each node and its values are all of the 
    nodes that can be reached from the key node, as well as the corresponding speed 
    of the way that connects the nodes. The second dictionary containes each node, as 
    well as a tuple of its location of form (lat, lon)
    """
    
    # initialize all of the dictionaries and lists
    waylist = []
    nodes_dict = {}
    loc_dict = {}
    speed_dict = {}
    
    # iterate through each way in the way file and check
    # if it is a valid highway, if it is, add it to the waylist
    for way in read_osm_data(ways_filename):
        try:
            if way["tags"]["highway"] in ALLOWED_HIGHWAY_TYPES:
                
                waylist.append(way)  
        except KeyError:
            waylist = waylist      
    
    #for each way in waylist, create nodes dict with the ways in waylist
    #add each node as a key with the nodes that can be reached as values, as well as the speed,
    # represented by a value of (node, speed). Adhere to oneway rules.
    for way1 in waylist:
        nodes = way1["nodes"]
        try:
            speed = way1["tags"]["maxspeed_mph"]
        except KeyError:
            speed = DEFAULT_SPEED_LIMIT_MPH[way1["tags"]["highway"]]    
        for i in range(len(nodes)):
            try:               
                if way1["tags"]["oneway"] == "yes":
                    if nodes[i] not in nodes_dict:
                        nodes_dict[nodes[i]] = set()
                    if i < len(nodes) - 1:
                        nodes_dict[nodes[i]].add((nodes[i+1], speed))
                else:
                    if nodes[i] not in nodes_dict:
                        nodes_dict[nodes[i]] = set()
                    if i < len(nodes) - 1:
                        nodes_dict[nodes[i]].add((nodes[i+1], speed))
                        if nodes[i+1] not in nodes_dict:
                            nodes_dict[nodes[i+1]] = set()
                        nodes_dict[nodes[i+1]].add((nodes[i], speed)) 
            except KeyError:
                if nodes[i] not in nodes_dict:
                    nodes_dict[nodes[i]] = set()
                if i < len(nodes) - 1:
                    nodes_dict[nodes[i]].add((nodes[i+1], speed))
                    if nodes[i+1] not in nodes_dict:
                        nodes_dict[nodes[i+1]] = set()
                    nodes_dict[nodes[i+1]].add((nodes[i], speed))
    
    # iterate through nodes, if node is in the nodes dict, then add it to the second dictionary
    # the location dict. The location dict has a key of node, and a value of the nodes location 
    # in the form (lat, lon)
    for n1 in read_osm_data(nodes_filename):   
        if n1["id"] in nodes_dict:
            loc_dict[n1["id"]] = (n1["lat"], n1["lon"])
    return (nodes_dict, loc_dict)# return the two dictionaries       

def find_closest_node(map_rep, loc1):
    """
    this function takes in a map representation, as well as a location,
    and returns the closest node to that location in the form of the node
    id and its location tuple
    """
    dist = (None, float("inf")) # set the node to none and dist to inf
    for key in map_rep[1]: #iterate through all of the keys in the location dictionary
        # find distance from input location to the current key location
        dist1 = great_circle_distance(loc1, map_rep[1][key]) 
        if dist1 < dist[1]: # if this distance is less than current distance, update distance
            dist = (key, dist1)
    return (dist[0],map_rep[1][dist[0]]) # return closest id


    



def find_short_path_nodes(map_rep, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    
    # initialize all dictionaries, sets, and lists
    visited = set() # keeps track of nodes that have been visited
    start = node1
    goal = node2
    parent_dict = {start: None} # dictionary of each node and its parent
    agenda = [(start, 0)]  # agenda dictionary
    dist_dict = {} # dictionary mapping each node to its distance from the start node
    dist_dict[start] = 0
    path = [] # list of the path
    expanded_count = 0
    while agenda: # while we still have paths to consider
        lowest_cost = min(agenda, key = lambda agenda:agenda[1]) # pop the lowest cost item
        agenda.remove(lowest_cost)
        parent = lowest_cost[0]
        if parent == goal: # if parent is the goal, return the path
            while goal != None:
                path.append(goal)
                goal = parent_dict[goal]
            path.reverse()
            print("expanded count", expanded_count)
            # return path
        if parent not in visited: # if parent not in visited, add it to visited
            visited.add(parent)
        else:
            continue # if it has been visited, move on the to the next item in agenda
        try:
            for child in list(map_rep[0][parent]): # iterate through each child
                if child[0] not in visited:
                    dist = great_circle_distance(map_rep[1][parent], map_rep[1][child[0]])+lowest_cost[1]
                    if child[0] not in dist_dict or dist < dist_dict[child[0]]: # if child is the best current path
                        parent_dict[child[0]] = parent # add the child and parent to parent dict
                        dist_dict[child[0]] = dist # update distance dict
                        agenda.append((child[0], dist)) # add child to agenda
                        expanded_count += 1
        except KeyError:
            agenda = agenda
    return None # return none if all possibble nodes have been exhasuetd


def find_short_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    ## this is essentialy the same as the find short nodes function.
    ## the only differences are that in order to initialize the start and 
    ## end goal, we must find the closes node to both of these locations.
    ## And the path returned does not contain the nodes ids, but rather the location of the 
    ## node. Additionaly, we use a heurisitc to speed up the search. This allows the search to 
    ## focuse on paths closer to the goal
    # The functionality is completely the same.
    
    
    start = find_closest_node(map_rep, loc1)[0]
    goal = find_closest_node(map_rep, loc2)[0]
    visited = set()
    parent_dict = {start: None}
    agenda = [(start, 0, 0)]  
    dist_dict = {}
    dist_dict[start] = 0
    path = []
    expanded_count = 0
    while agenda:
        lowest_cost = min(agenda, key = lambda agenda:agenda[1]+agenda[2])
        agenda.remove(lowest_cost)
        parent = lowest_cost[0]
        if parent == goal:
            print("expanded count w heuristic ", expanded_count)
            while goal != None:
                path.append(map_rep[1][goal])
                goal = parent_dict[goal]
            path.reverse()
            # return path
        if parent not in visited:
            visited.add(parent)
        else:
            continue
        try:
            for child in list(map_rep[0][parent]):
                if child[0] not in visited:
                    heuristic = great_circle_distance(map_rep[1][child[0]], map_rep[1][goal])
                    dist = great_circle_distance(map_rep[1][parent], map_rep[1][child[0]])+lowest_cost[1]
                    if child[0] not in dist_dict or dist < dist_dict[child[0]]:
                        parent_dict[child[0]] = parent
                        dist_dict[child[0]] = dist
                        agenda.append((child[0], dist, heuristic))
                        expanded_count += 1
        except KeyError:
            agenda = agenda
    return None


def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    ## this is essentialy the same as the find short nodes function.
    ## the only differences are that in order to initialize the start and 
    ## end goal, we must find the closes node to both of these locations.
    ## The path returned does not contain the nodes ids, but rather the location of the 
    ## node. Additionaly, we are not using distance as our cost, but rather time, which is 
    ## calculated by distance divided by the speed.
    # The functionality is completely the same.
    
    start = find_closest_node(map_rep, loc1)[0]
    goal = find_closest_node(map_rep, loc2)[0]
    visited = set()
    parent_dict = {start: None}
    agenda = [(start, 0)]  
    time_dict = {}
    time_dict[start] = 0
    path = []
    while agenda:
        lowest_cost = min(agenda, key = lambda agenda:agenda[1])
        agenda.remove(lowest_cost)
        parent = lowest_cost[0]
        if parent == goal:
            while goal != None:
                path.append(map_rep[1][goal])
                goal = parent_dict[goal]
            path.reverse()
            return path
        if parent not in visited:
            visited.add(parent)
        else:
            continue
        try:
            for child in list(map_rep[0][parent]):
                if child[0] not in visited:
                    time = (great_circle_distance(map_rep[1][parent], map_rep[1][child[0]]))/child[1]+lowest_cost[1]
                    if child[0] not in time_dict or time < time_dict[child[0]]:
                        parent_dict[child[0]] = parent
                        time_dict[child[0]] = time
                        agenda.append((child[0], time))
        except KeyError:
            agenda = agenda
    return None
    

if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
