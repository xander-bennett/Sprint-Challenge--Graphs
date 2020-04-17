from room import Room
from player import Player
from world import World
from util import Queue

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']

#CODE BEGINS HERE

#Prior to traversing the entire map, we need to understand which rooms are connected to each other.
#To do this, we shall start in our starting room, and check which rooms are connected to it
#those connected rooms are then recursively evaluated until the entire grid is populated

#this works because all rooms are connected in one larger graph

def room_recursive(starting_room,room_graph,room_paths=None,visited=None):
    '''
    This function shows the path of how rooms are connected together.
    starting_room = The node in the graph we are evaluating neighbors of
    room_graph = The overall map of the adventure maze we are exploring
    room_paths = The linked paths that a room can lead to, default value of None.
        Populated on a per room basis during the recursive search
    visited = The list of rooms that have been searched
    '''
    
    #Initialize an empty list
    if visited is None:
        visited = []
    #initialize room paths
    if room_paths is None:
        room_paths = {}
    #obtain the current room id
    room_id = starting_room.id
    #if that room ID isn't in the room_paths dict
    if room_id not in room_paths.keys():
        #append room ID to the visited list
        visited.append(room_id)
        #and then add this room as a key in the path dictionary
        room_paths[room_id] = {}
        #grab the viable exits for that starting room.
        directions = starting_room.get_exits()
        #for each direction the room has...
        for dir in directions:
            #update the path dictionary so at the key of the room ID
            #Each direction the room has from the get_exits function
            #attach that direction, and the ID of the connected room
            room_paths[room_id].update({dir:starting_room.get_room_in_direction(dir).id})
        #shuffle the directions a room has to have a non-deterministic crawl
        directions = starting_room.get_exits()
        random.shuffle(directions)
        #for each direction our starting_room has connected to it
        #walk the path to that new room
        for direction in directions:
            new_room = starting_room.get_room_in_direction(direction)
            #recursively apply the same logic above to the next room!
            room_recursive(new_room,room_graph,room_paths,visited)
        if len(room_paths) == len(room_graph):
            return room_paths,visited

def bfs(starting_room, destination_room,room_paths):
    """
    Using Breadth First Search
    This will return the shortest path between a starting room
    and a destination room
    starting_room = Room ID of starting room
    destination_room = Room ID of destination room.
    room_paths = The linked paths that a room can lead to, default value of None.
        (generated from recursive_room_population function)
    """
    #create a set of visited rooms:
    #keeping track of previously visited rooms will expedite the bfs.
    visited = set()
    #setting up a queue of rooms to explore
    #a queue is used since it is first in first out
    #a queue will accomplish finding the shortest path because of its use of a queue
    room_queue = Queue()

    #direction queue will receive the applicable directions
    dir_queue = Queue()

    #the queue is initialized with the starting room
    room_queue.enqueue([starting_room])
    #the direction queue is initialized as a blank list
    # but will be populated shortly with movement
    dir_queue.enqueue([])
    
    #while there are rooms in the queue...
    while room_queue.size() > 0:
        #take the next value in the queue
        vertex_path = room_queue.dequeue()
        #take the next direction to travel in that queue
        dir_path = dir_queue.dequeue()
        #The most recent room in the room_path taken from the queue
        #is the newest room that's been explored
        vertex = vertex_path[-1]
        #if that room has not been visited before
        if vertex not in visited:
            visited.add(vertex)
            #if the new room is the desired destination
            if vertex == destination_room:
                return dir_path
            #then, for each direction that a room has mapped to it in the room_path dictionary
            for direction in room_paths[vertex]:
                #copy the room_path and travel_path queues.
                path_copy = vertex_path.copy()
                dirpath_copy = dir_path.copy()
                
                #add the newest room and directions to the copied room_path route
                path_copy.append(room_paths[vertex][direction])
                dirpath_copy.append(direction)
                room_queue.enqueue(path_copy)
                dir_queue.enqueue(dirpath_copy)



#initialize the answer list of traversal path
traversal_path = []
#set the player in the world's starting room
player = Player(world.starting_room)
#visit all rooms recursively
room_dict,visited = room_recursive(world.starting_room,room_graph)

#for each room in the visited list
for i in range(len(visited)-1):
    #use bfs to find shortest pathway between two rooms
    path = bfs(visited[i],visited[i+1],room_dict)
    #add the path of the navigation between those two rooms to the traversal path list
    traversal_path.extend(path)



# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")

#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")