# Imports
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
        self.defaultReward      = -0.25    # For cells with no food
        self.defaultFoodReward  = -0.01    # For cells with food
        self.defaultGhostReward = -0.25    # For cells with ghosts
        self.discount           = 0.75    # Discount for Bellmans Equation
        self.dangerDistance     = 3    # How many cells away should a ghost be before pacman feels unsafe?


    def getMap(self, x, y):
        ''' Returns map of environment'''
        return self.worldMap[y][x]


    def setMap(self, x, y, attr, val):
        ''' Set value of map, attr is utility, reward, type, temp'''
        self.worldMap[int(y)][int(x)][attr] = val


    def copy(self):
        '''Copies values in temp to utility for each cell in map'''
        for y in range(self.height):
            for x in range(self.width):
                temp = self.getMap(x, y)["temp"]
                self.setMap(x, y, "utility", temp)


    def isEqual(self):
        ''' Checks if values in utility and values in temp are'''
        for y in range(self.height):
            for x in range(self.width):
                if (self.getMap(x, y)["utility"] != self.getMap(x, y)["temp"]): return False
        return True


    def isWall(self, x, y):
        ''' Checks if given location in map is a wall'''
        if (self.getMap(x, y)['type'] == "W"): return True
        else: return False


    def hasFood(self, x, y):
        ''' Checks if given location in map has a food item'''
        if (self.getMap(x, y)['type'] == "F"): return True
        else: return False


    def getUtility(self, x, y):
        '''Get utility value of given location'''
        return self.getMap(x, y)['utility']


    def printMap(self, attr = "type"):

        # Print Empty Line between Maps
        print "\n"

        # Print contents of each coordinate
        for y in range(len(self.worldMap) -1 , -1, -1):
            for x in range(0, len(self.worldMap[self.height - 1])):
                if (x == len(self.worldMap[0]) - 1): print self.format(self.worldMap[y][x][attr])
                else: print self.format(self.worldMap[y][x][attr]),


    def format(self, val):

        ''' Colourise printout and add symbols'''

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



    def registerInitialState(self, state):

        '''This method is run upon starting the program'''

        # Update State of World
        self.updateState(state)

        # Calculate Height of World
        self.width   = self.corners[3][0] + 1
        self.height  = self.corners[3][1] + 1

        # Generate a World Map
        self.generateWorldMap()

        # Update state of Map
        self.updateMap()

        
    def final(self, state):

        '''This method is run when the game ends.'''

        print "The game ended."


    def generateWorldMap(self):

        '''Generates a world map represented by a 2D array, each cell contains a type, utility, reward, policy and temp value.'''

        # Generate an empty dictionary of values to store in each cell of the worldMap
        emptyDictionary = {'type': 'E', 'utility': 0, 'reward': self.defaultReward, 'policy': Directions.STOP, 'temp': 0 }

        # Generate a row of length self.width
        row = [emptyDictionary for x in range(self.width)]

        # Generate columns by replicating rows to generate world map.
        self.worldMap = [[emptyDictionary.copy() for x in range(self.width)] for y in range(self.height)] 

    
    def updateMap(self): 

        ''' Updates type, reward, utility of cells in map,
            This is run per cycle of each game so that all moves are kept up to date,
            For example, the location of the ghosts are always known'''

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
        for food in self.foods: self.setMap(food[0], food[1], "reward", self.defaultFoodReward)

        # Place ghosts on map
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "type", "G")
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "utility", 0.5)
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "temp", 0.5)
        for ghost in self.ghosts: self.setMap(ghost[0], ghost[1], "reward", self.defaultGhostReward)
        
        # Place capsule on map
        for capsule in self.capsules: self.setMap(capsule[0], capsule[1], "type", "C")


    def valueIteration(self, state):

        '''Performs value iteration until convergence on the map'''
        
        # Update utilities
        self.updateUtilities(state)

        # Converge
        while (not self.isEqual()):
            self.copy()
            self.updateUtilities(state)


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


    def getGhostsAndStates(self, state, distance):

        ''' Get ghosts within a certain distance, will return an array of ghost locations with its status
            (Whether it is active or not)'''

        # Get List of Ghosts within certain area.
        ghosts = api.distanceLimited(self.ghosts, state, distance)

        # Get List of Ghosts with States in whole map.
        ghostStates = api.ghostStates(state)

        # Temporary List to Return Dangerous Ghosts in specified area.
        dangerousGhosts = []

        # Find dangerous ghosts and add to dangerous ghosts list
        if (len(ghosts) != 0):
            for ghost in ghosts:
                for ghostState in ghostStates:
                      if (ghost == ghostState[0]):
                          dangerousGhosts.append(ghostState)

        return dangerousGhosts


    def removeDangerousDirections(self, state, dangerousGhosts): 

        ''' Given a list of dangerous ghosts, remove directions from possible moves that might endanger pacman'''

        # Do for each dangerous ghost
        for i in range(len(dangerousGhosts)):

            # If ghost is north of agent
            if dangerousGhosts[i][0][1] > self.currentLocation[1]:
                if Directions.NORTH in self.legal:
                    self.legal.remove(Directions.NORTH)

            # If ghost is south of agent
            if dangerousGhosts[i][0][1] < self.currentLocation[1] :
                    if Directions.SOUTH in self.legal:
                        self.legal.remove(Directions.SOUTH)

            # If ghost is west of agent
            if dangerousGhosts[i][0][0] < self.currentLocation[0] :
                    if Directions.WEST in self.legal:
                        self.legal.remove(Directions.WEST)

            # If ghost is east of agent
            if dangerousGhosts[i][0][0] > self.currentLocation[0]:
                    if Directions.EAST in self.legal:
                        self.legal.remove(Directions.EAST)


    def getAction(self, state):

        '''Method is run per cycle in a game, determines which direction the pacman will go'''


        # Print map rep to the console
        # self.printMap()

        # Update State of World
        self.updateState(state)

        # Update Map
        self.updateMap()

        # Update utilities
        self.valueIteration(state)

        # Get utilty of current location
        currentUtility = self.getMap(self.currentLocation[0], self.currentLocation[1])['utility']

        # Get all ghosts within a specific area
        dangerousGhosts = self.getGhostsAndStates(state, self.dangerDistance)

        # Remove ghosts from lists that aren't actively dangerous.
        for ghost in dangerousGhosts:
            if (ghost[1] == 1): dangerousGhosts.remove(ghost)
            
        # Remove dangerous ghosts
        self.removeDangerousDirections(state, dangerousGhosts)
       
        # If only one way pacman can go, don't waste time by stopping.
        if len(self.legal) == 2 and Directions.STOP in self.legal:
            self.legal.remove(Directions.STOP)
            move = random.choice(self.legal)

        # Get utility of the resulting cell for each possible action, otherwise, the utility will be set to current cell.
        else:
            if (self.getMap(self.currentLocation[0]+1, self.currentLocation[1])['utility'] != 'W'): east = self.getMap(self.currentLocation[0]+1, self.currentLocation[1])
            else: east = currentUtility

            if (self.getMap(self.currentLocation[0]-1, self.currentLocation[1])['utility'] != 'W'): west = self.getMap(self.currentLocation[0]-1, self.currentLocation[1])
            else: west = currentUtility

            if (self.getMap(self.currentLocation[0], self.currentLocation[1] + 1)['utility'] != 'W'): north = self.getMap(self.currentLocation[0], self.currentLocation[1] + 1)
            else: north = currentUtility

            if (self.getMap(self.currentLocation[0], self.currentLocation[1] - 1)['utility'] != 'W'): south = self.getMap(self.currentLocation[0], self.currentLocation[1] - 1)
            else: south = currentUtility


            # Add all utility values of all possible actions. Only add if legally allowed.
            legal = []
            if Directions.SOUTH in self.legal: legal.append(south)
            if Directions.NORTH in self.legal: legal.append(north)
            if Directions.EAST in self.legal: legal.append(east)
            if Directions.WEST in self.legal: legal.append(west)
 
            # If no legal moves, then stop.
            if 	len(legal) == 0: move = Directions.STOP

            # Get move with highest utility and set move if legal.
            elif max(legal) == south and Directions.SOUTH in self.legal: move = Directions.SOUTH
            elif max(legal) == north and Directions.NORTH in self.legal: move = Directions.NORTH
            elif max(legal) == west and Directions.WEST in self.legal: move = Directions.WEST
            elif max(legal) == east and Directions.EAST in self.legal: move = Directions.EAST

            # else make random move
            else: move = random.choice(api.legalActions(state))

        # Make move
        return api.makeMove(move, api.legalActions(state))


    def updateUtilities(self, state):

        ''' Updates the utilities of the map'''

        # Update utility for every cell in map.
        for y in range(self.height):
            for x in range(self.width):

                # No need to update utilty if cell is a wall or has food as we have assume default values.
                if (not self.isWall(x, y) and not self.hasFood(x, y)):
                    
                    # Get utility of cell
                    utility = self.getUtility(x, y)

                    # Set resulting utilities for all actions
                    e = w = s = n = utility

                    # Get utilities for resulting cells for all actions.
                    if (not self.isWall(x, y + 1)): n = self.getUtility(x, y + 1)

                    if (not self.isWall(x, y - 1)): s = self.getUtility(x, y - 1)
                
                    if (not self.isWall(x + 1, y)): e = self.getUtility(x + 1, y)

                    if (not self.isWall(x - 1, y)): w = self.getUtility(x - 1, y)

                    # Apply non determinsim to find expected utility.
                    u = (0.8 * n) + (0.1 * e) + (0.1 * w)
                    l = (0.8 * e) + (0.1 * n) + (0.1 * s)
                    r = (0.8 * w) + (0.1 * n) + (0.1 * s)
                    d = (0.8 * s) + (0.1 * e) + (0.1 * w)

                    # Set and update utilities
                    utility = self.getMap(x, y)['reward'] + (self.discount * max(u, l, r, d))
                    self.setMap(x, y, "temp", utility)

    


    










