

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        self.discountFactor = 1
        self.worldMap = None
        self.foodReward = 0.3
        self.ghostReward = -1
        self.wallReward = -0.5
        self.capsuleReward = 0.5
        self.meReward = -0.2
        self.emptyReward = -0.1

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        self.updateMap(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"



    # For now I just move randomly
    def getAction(self, state):

        # Get Legal Actions
        legal = api.legalActions(state)

        # Get Current Location
        currentLocation = api.whereAmI(state)

        # Get Corners
        corners = api.corners(state)

        # Get Food
        foods = api.food(state)

        # Get Ghosts
        ghosts = api.ghosts(state)

        # Get Capsules
        capsules = api.capsules(state)

        # Get Walls
        walls = api.walls(state)

        # Calculate Height of World

        # Get a usable representation of the world.
        self.updateMap(state)
        self.printUtility()


        for y in range(0, len(self.worldMap)):
            for x in range(0, len(self.worldMap[y])):
                for i in range(0, 10):
                    self.setUtility(x, y, self.getReward(x,y) + self.policyEvaluation(x, y))

        # Random choice between the legal options.
        return api.makeMove(self.getPolicy(currentLocation[0], me[1]), legal)



    def policyEvaluation(self, x, y):

        if (self.getPolicy(x, y) == Directions.STOP):
            return self.getUtility(x, y)

        return None












    def printReward(self):
        self.printWorld(1)

    def printUtility(self):
        self.printWorld(2)

    def printMap(self):
        self.printWorld(0)

    def printPolicy(self):
        self.printWorld(3)

    def setMap(self, x, y, val):
        self.worldMap[int(y)][int(x)] = val

    def setUtility(self, col, row, val):
        self.worldMap[int(row)][int(col)][2] = val

    def getUtility(self, col, row):
        return self.worldMap[row][col][2]

    def setReward(self, col, row, val):
        self.worldMap[int(row)][int(col)][1] = val

    def getReward(self, col, row):
        return self.worldMap[row][col][1]

    def setPolicy(self, col, row, val):
        self.worldMap[int(row)][int(col)][3] = val

    def getPolicy(self, col, row):
        return self.worldMap[row][col][3]

    def setThing(self, row, col, val):
        self.worldMap[int(row)][int(col)][0] = val

    def getThing(self, col, row):
        return self.worldMap[int(row)][int(col)][0]


    def updateMap(self, state):

        corners = api.corners(state)
        ghosts = api.ghosts(state)
        me = api.whereAmI(state)
        walls = api.walls(state)
        capsules = api.capsules(state)
        foods = api.food(state)
        
        # Width and Height of Map
        width, height = corners[3][0] + 1, corners[3][1] + 1
        
        # Generate empty world Map
        if (self.worldMap is None):
            self.worldMap = [[[' ', self.emptyReward, 0, Directions.STOP] for x in range(width)] for y in range(height)] 

            self.setMap(me[0], me[1], ['M', self.meReward, 0, Directions.STOP])
            for food in foods: self.setMap(food[0], food[1], ['F', self.foodReward, 0, Directions.STOP])
            for capsule in capsules: self.setMap(capsule[0], capsule[1], ['C', self.capsuleReward, 0, Directions.STOP])
            for wall in walls: self.setMap(wall[0], wall[1], ['W', self.wallReward, 0, Directions.STOP])
            for ghost in ghosts: self.setMap(ghost[0], ghost[1], ['G', self.ghostReward, 0, Directions.STOP])

        else: 
            self.clearMapKeepState(state)
            self.setThing(me[1], me[0], 'M')
            for food in foods: self.setThing(food[1], food[0], 'F')
            for capsule in capsules: self.setThing(capsule[1], capsule[0], 'C')
            for wall in walls: self.setThing(wall[1], wall[0], 'W')
            for ghost in ghosts: self.setThing(ghost[1], ghost[0], 'G')
            self.setReward(me[0], me[1], self.meReward)
            for food in foods: self.setReward(food[0], food[1], self.foodReward)
            for capsule in capsules: self.setReward(capsule[0], capsule[1], self.capsuleReward)
            for wall in walls: self.setReward(wall[0], wall[1], self.wallReward)
            for ghost in ghosts: self.setReward(ghost[0], ghost[1], self.ghostReward)


    def clearMapKeepState(self, state):
        for row in range(0, len(self.worldMap)):
            for col in range(0, len(self.worldMap[row])):
                self.setThing(row, col, ' ')
                self.setReward(col, row, self.emptyReward)




















    def printWorld(self, index):

        # Print Empty Line between Maps
        print "\n"

        # Print contents of each coordinate
        for i in range(len(self.worldMap)-1, -1, -1):
            for j in range(0, len(self.worldMap[0])):
                if (j == len(self.worldMap[0]) - 1): print self.colour(self.worldMap[i][j][index])
                else: print self.colour(self.worldMap[i][j][index]),

    def colour(self, val):

        val = str(val)

        if (val == 'M'): return '\033[36m' + u'\u2588' + '\033[0m'
        if (val == 'E'): return '\033[36m' + val + '\033[0m'
        if (val == 'W'): return '\033[93m' + u'\u2588' + '\033[0m'
        if (val == 'G'): return '\033[91m' + u'\u271B' + '\033[0m'
        if (val == 'F'): return '\033[92m' + u'\u25cc' + '\033[0m'
        if (val == 'C'): return u'\u25CF'
        return val

