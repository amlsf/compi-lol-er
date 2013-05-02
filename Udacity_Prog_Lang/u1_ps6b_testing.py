# Title: Reading Machine Minds

# It can be difficult to predict what strings a finite state machine will
# accept. A tricky finite state machine may not accept any! A finite state
# machine that accepts no strings is said to be *empty*. 
# 
# In this homework problem you will determine if a finite state machine is
# empty or not. If it is not empty, you will prove that by returning a
# string that it accepts. 
#
# Formally, you will write a procedure nfsmaccepts() that takes four
# arguments corresponding to a non-derministic finite state machine:
#   the start (or current) state
#   the edges (encoded as a mapping)
#   the list of accepting states
#   a list of states already visited (starts empty) 
#
# If the finite state machine accepts any string, your procedure must
# return one such string (your choice!). Otherwise, if the finite state
# machine is empty, your procedure must return None (the value None, not
# the string "None"). 
#
# For example, this non-deterministic machine ...
edges = { (1, 'a') : [2, 3],
          (2, 'a') : [2],
          (3, 'b') : [4, 2],
          (4, 'c') : [5] }
accepting = [5] 
# ... accepts exactly one string: "abc". By contrast, this
# non-deterministic machine: 
edges2 = { (1, 'a') : [1],
           (2, 'a') : [2] }
accepting2 = [2] 
# ... accepts no strings (if you look closely, you'll see that you cannot
# actually reach state 2 when starting in state 1). 

# Hint #1: This problem is trickier than it looks. If you do not keep track
# of where you have been, your procedure may loop forever on the second
# example. Before you make a recursive call, add the current state to the
# list of visited states (and be sure to check the list of visited states
# elsewhere). 
#
# Hint #2: (Base Case) If the current state is accepting, you can return
# "" as an accepting string.  
# 
# Hint #3: (Recursion) If you have an outgoing edge labeled "a" that
# goes to a state that accepts on the string "bc" (i.e., the recursive call
# returns "bc"), then you can return "abc". 
#
# Hint #4: You may want to iterate over all of the edges and only consider
# those relevant to your current state. "for edge in edges" will iterate
# over all of the keys in the mapping (i.e., over all of the (state,letter)
# pairs) -- you'll have to write "edges[edge]" to get the destination list. 

route = []
def nfsmaccepts(current, edges, accepting, visited): 
        # write your code here
    global route
    # BASE CASE: if current state is accepting
    print "current: ", current, "accepting: ", accepting
    if current in accepting:
        string = ""
        if current != 1:
            for state in route:
                string += state[1]
        print string
        return string

    # add edge key to "visited"
    for key in iter(edges):
        if key[0] == current:
            current_char = key[1]
            visited.append(current)
            route.append((current, current_char))
            print "route:", route
            break
    
    # recursively call for ALL options in values matching the current key
    # if the value is the same as the current, return
    if current_char:
        for next_state in edges[current, current_char]:
	        # do I need to change this so that i'm looping through visited and finding
	        # if next_state is IN visited? it would solve the same problem, but what
	        # are the edge cases in which one of the 2 methods would fail?
	        # YEP, in edge (3,'b'), 2 is a potential route, but you've already visited it.
            print "next state:", next_state
            if next_state == current:
                print "The potential route", next_state, "is the same as the current state", current, "so take this off the official route list."
                route.pop()
                return
            print "visited:", visited
            for been_there in visited:
                print 1
                if next_state == been_there:
                    print "The potential route", next_state, "has already been visited as it's in the list:", visited, "so don't go there."
                    continue
                else:
                    x = nfsmaccepts(next_state, edges, accepting, visited)
                    if x:
                        return x
    else:
        return	        

# This problem includes some test cases to help you tell if you are on
# the right track. You may want to make your own additional tests as well.
print "Test 1: " + str(nfsmaccepts(1, edges, accepting, []) == "abc") 
route = []
print "Test 2: " + str(nfsmaccepts(1, edges, [4], []) == "ab") 
route = []
print "Test 3: " + str(nfsmaccepts(1, edges2, accepting2, []) == None) 
route = []
print "Test 4: " + str(nfsmaccepts(1, edges2, [1], []) == "")