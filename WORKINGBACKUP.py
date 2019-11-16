

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):

        self.legal              = None
        self.currentLocation    = None
        self.corners            = None
        self.foods              = None
        self.ghosts             = None
        self.capsules           = None
        self.walls              = None
        self.height             = None
        self.width              = None
        self.worldMap           = None
        self.defaultReward      = -0.01
        self.discount           = 0.8


    def registerInitialState(self, state):

        # Update State of World
        self.updateState(state)

        # Calculate Height of World
        self.width   = self.corners[3][0] + 1
        self.height  = self.corners[3][1] + 1

        # Generate a World Map
        self.generateWorldMap()

        # Update state of Map
        self.updateMap()
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # For now I just move randomly
    def getAction(self, state):

        # Update State of World
        self.updateState(state)

        # Update Map
        self.updateMap()

        # Update utilities
        self.updateUtilities(state)

        # Converge
        while (not self.isEqual()):
            self.copy()
            self.updateUtilities(state)

        ghostlist = api.distanceLimited(self.ghosts, state, 3)
        myvalue = self.getMap(self.currentLocation[0], self.currentLocation[1])['utility']
        mystate = self.currentLocation

        if (ghostlist):
             for i in range(len(ghostlist)):
                if ghostlist[i][1] > self.currentLocation[1] :
                    if Directions.NORTH in self.legal:
                            self.legal.remove(Directions.NORTH)
    
                if ghostlist[i][1] < mystate[1] :
                        if Directions.SOUTH in self.legal:
                            self.legal.remove(Directions.SOUTH)
        
                if ghostlist[i][0] < mystate[0] :
                        if Directions.WEST in self.legal:
                            self.legal.remove(Directions.WEST)
            
                if ghostlist[i][0] > mystate[0]:
                        if Directions.EAST in self.legal:
                            self.legal.remove(Directions.EAST)

        
        if len(self.legal) == 2 and Directions.STOP in self.legal:
            self.legal.remove(Directions.STOP)
            goto = random.choice(self.legal)

        else:

            if (self.getMap(mystate[0]+1, mystate[1])['utility'] != 'W'):
                myeast = self.getMap(mystate[0]+1, mystate[1])
            else: myeast = myvalue

            if (self.getMap(mystate[0]-1, mystate[1])['utility'] != 'W'):
                mywest = self.getMap(mystate[0]-1, mystate[1])
            else: mywest = myvalue

            if (self.getMap(mystate[0], mystate[1] + 1)['utility'] != 'W'):
                mynorth = self.getMap(mystate[0], mystate[1] + 1)
            else: mynorth = myvalue

            if (self.getMap(mystate[0], mystate[1] - 1)['utility'] != 'W'):
                mysouth = self.getMap(mystate[0], mystate[1] - 1)
            else: mysouth = myvalue


            mylist = []
            if Directions.EAST in self.legal:
                mylist.append(myeast)
            if Directions.SOUTH in self.legal:
                mylist.append(mysouth)
            if Directions.NORTH in self.legal:
                mylist.append(mynorth)
            if Directions.WEST in self.legal:
                mylist.append(mywest)
 
            if 	len(mylist) == 0:
                goto = Directions.STOP

            elif max(mylist) == myeast and Directions.EAST in self.legal:
                goto = Directions.EAST
            elif max(mylist) == mysouth and Directions.SOUTH in self.legal:
                goto = Directions.SOUTH
            elif max(mylist) == mywest and Directions.WEST in self.legal:
                goto = Directions.WEST
            elif max(mylist) == mynorth and Directions.NORTH in self.legal:
                goto = Directions.NORTH
            # if pacman cannot make decision, just make a random choice
            else: goto = random.choice(api.legalActions(state))

        return api.makeMove(goto, api.legalActions(state))


    # In each element in the world map: [0, 1, 2, 3, 4, 5]
    def generateWorldMap(self):

        # Generate an empty dictionary of values to store in each cell of the worldMap
        emptyDictionary = {'type': 'E', 'utility': 0, 'reward': self.defaultReward, 'policy': Directions.STOP, 'temp': 0 }

        # Generate a row of length self.width
        row = [emptyDictionary for x in range(self.width)]

        # Generate columns by replicating rows to generate world map.
        self.worldMap = [[emptyDictionary.copy() for x in range(self.width)] for y in range(self.height)] 

    
    def updateMap(self): 

        # Assume all cells in world are empty
        self.clearWorldMap("type")

        # Assume all cells in world have default reward
        self.clearWorldMap("reward")
        
        # Assume all cells in world have default utility
        self.clearWorldMap("utility")

        # Place current location on map
        self.setMap(self.currentLocation[0], self.currentLocation[1], "type", "M")

        # Place walls on map
        for wall in self.walls: self.setMap(wall[0], wall[1], "type", "W")
        for wall in self.walls: self.setMap(wall[0], wall[1], "utility", "W")
        for wall in self.walls: self.setMap(wall[0], wall[1], "temp", "W")

        # Place food on map
        for food in self.foods: self.setMap(food[0], food[1], "type", "F")
        for food in self.foods: self.setMap(food[0], food[1], "utility", 1)
        for food in self.foods: self.setMap(food[0], food[1], "temp", 1)

        # Place ghosts on map
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "type", "G")
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "utility", 0.5)
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "temp", 0.5)
        

        # Place capsule on map
        for capsule in self.capsules: self.setMap(capsule[0], capsule[1], "type", "C")


    def updateUtilities(self, state):

        for y in range(self.height):
            for x in range(self.width):
                if (self.getMap(x, y)['utility'] != "W" and self.getMap(x, y)['utility'] != 1):
                    
                    utility = self.getMap(x, y)['utility']
                
                    if (self.getMap(x + 1, y)['utility'] != 'W'): east = self.getMap(x + 1, y)['utility']
                    else: east = utility

                    if (self.getMap(x - 1, y)['utility'] != 'W'): west = self.getMap(x - 1, y)['utility']
                    else: west = utility

                    if (self.getMap(x, y + 1)['utility'] != 'W'): north = self.getMap(x, y + 1)['utility']
                    else: north = utility

                    if (self.getMap(x, y - 1)['utility'] != 'W'): south = self.getMap(x, y - 1)['utility']
                    else: south = utility

                    up = 0.8 * north + 0.1 * east + 0.1 * west
                    left = 0.8 * east + 0.1 * north + 0.1 * south
                    right = 0.8 * west + 0.1 * north + 0.1 * south
                    down = 0.8 * south + 0.1 * east + 0.1 * west

                    utility = self.getMap(x, y)['reward'] + (self.discount * max(up,left,right,down))
                    self.setMap(x, y, "temp", utility)

       
       
       


    def getMap(self, x, y):
        return self.worldMap[y][x]

    def setMap(self, x, y, attr, val):
        self.worldMap[int(y)][int(x)][attr] = val

    def copy(self):
         for y in range(self.height):
            for x in range(self.width):
                temp = self.getMap(x, y)["temp"]
                self.setMap(x, y, "utility", temp)

    def isEqual(self):
        for y in range(self.height):
            for x in range(self.width):
                if (self.getMap(x, y)["utility"] != self.getMap(x, y)["temp"]): return False
        return True

    def isWall(self, x, y):
        if (self.getMap(x, y)['type'] == "W"): return True
        else: return False

    def hasFood(self, x, y):
        if (self.getMap(x, y)['type'] == "F"): return True
        else: return False



    def updateState(self, state):

        # Update Legal Moves
        self.legal = api.legalActions(state)

        # Update Current Location
        self.currentLocation = api.whereAmI(state)

        # Update Position of Corners
        self.corners = api.corners(state)

        # Update Position of Food
        self.foods = api.food(state)

        # Update Position of Ghosts
        self.ghosts = api.ghosts(state)

        # Update Position of Capsules
        self.capsules = api.capsules(state)

        # Update Position of Walls
        self.walls = api.walls(state)


    def printMap(self, attr = "type"):

        # Print Empty Line between Maps
        print "\n"

        # Print contents of each coordinate
        for y in range(len(self.worldMap) -1 , -1, -1):
            for x in range(0, len(self.worldMap[self.height - 1])):
                if (x == len(self.worldMap[0]) - 1): print self.format(self.worldMap[y][x][attr])
                else: print self.format(self.worldMap[y][x][attr]),


    def format(self, val):

        val = str(val)

        if (val == 'M'): return '\033[36m' + u'\u2588' + '\033[0m'
        if (val == 'E'): return '\033[36m' + ' ' + '\033[0m'
        if (val == 'W'): return '\033[93m' + u'\u2588' + '\033[0m'
        if (val == 'G'): return '\033[91m' + u'\u271B' + '\033[0m'
        if (val == 'F'): return '\033[92m' + u'\u25cc' + '\033[0m'
        if (val == 'C'): return u'\u25CF'
        return val


    def clearWorldMap(self, attr="all"):

        for y in range(0, len(self.worldMap)):
            for x in range(0, len(self.worldMap[self.height - 1])):
                if (attr == "all" or attr == "type"): self.worldMap[y][x]['type'] = "E"
                if (attr == "all" or attr == "utility"): self.worldMap[y][x]['utility'] = 0
                if (attr == "all" or attr == "policy"): self.worldMap[y][x]['policy'] = Directions.STOP
                if (attr == "all" or attr == "reward"): self.worldMap[y][x]['reward'] = self.defaultReward
                if (attr == "all" or attr == "temp"): self.worldMap[y][x]['temp'] = 0



    










