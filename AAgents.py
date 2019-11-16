
from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys
#set a number as reward
reward = -0.01
#set a number as discount
discount = 1
# set a distance that packman feeling danger
danger = 3
#set a glable value to save the number of food
numoffood = 0

#build map
class Grid:
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # print map at terminal.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width



class MDPAAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        name = "Pacman"

    def registerInitialState(self, state):

        global numoffood
        numoffood = len(api.food(state))

        self.makeMap(state)
        self.addWallsFoodToMap(state)




    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        height = corners[3][1] + 1
        width  = corners[3][0] + 1
        self.map1 = Grid(width, height)
        self.map2 = Grid(width, height)


    # Functions to manipulate two same new map.
    # Put every element in the list of wall  and the list of food into the two maps
    def addWallsFoodToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map1.setValue(walls[i][0], walls[i][1], '%')
            self.map2.setValue(walls[i][0], walls[i][1], '%')
        food = api.food(state)

        for i in range(len(food)):
            self.map1.setValue(food[i][0], food[i][1],1)
            self.map2.setValue(food[i][0], food[i][1],1)




    # using current utilities in map1 to calculate the new utility of each grid without wall and food
    # save the new utilities we just calculated to the map2
    def updateMap(self, state):


        for i in range(self.map1.getWidth()):
            for j in range(self.map1.getHeight()):
                if self.map1.getValue(i, j) != '%'and self.map1.getValue(i, j) != 1 :

                    thevalue = self.map1.getValue(i, j)
        

                  
                    if (self.map1.getValue(i+1, j) != '%'):
                        theeast = self.map1.getValue(i+1, j)
                    else: theeast = thevalue

                    if (self.map1.getValue(i-1, j) != '%'):
                        thewest = self.map1.getValue(i-1, j)
                    else: thewest = thevalue

                    if(self.map1.getValue(i, j+1) != '%'):
                        thenorth = self.map1.getValue(i, j+1)
                    else: thenorth = thevalue

                    if(self.map1.getValue(i, j-1) != '%'):
                        thesouth = self.map1.getValue(i, j-1)
                    else: thesouth = thevalue

                    up = 0.8 * thenorth + 0.1 * theeast + 0.1 * thewest
                    left = 0.8 * theeast + 0.1 * thenorth + 0.1 * thesouth
                    right = 0.8 * thewest + 0.1 * thenorth + 0.1 * thesouth
                    down = 0.8 * thesouth + 0.1 * theeast + 0.1 * thewest

                    thevalue = reward + (discount * max(up,left,right,down))
                    self.map2.setValue(i,j, thevalue)




    def getAction(self, state):

        #compare previous number of food and current number of food
        global numoffood
        if numoffood != len(api.food(state)):
           numoffood = len(api.food(state))
          #Remake maps
           self.makeMap(state)
           self.addWallsFoodToMap(state)
           
        #
        #the new utilitis saved in the map2 in the FUNCTION self.updateMap(state)
        self.updateMap(state)
        #calculate the utility for map1, until the utilitis does not change anymore
        while (self.map1 != self.map2):

        # so updated utilitis in map1
            self.map1 = self.map2
            self.updateMap(state)

        self.map1.prettyDisplay()



        # get current pacman state and value
        mystate = api.whereAmI(state)
        #get my value
        myvalue = self.map1.getValue(mystate[0], mystate[1])
        #Get the actions we can try
        legal = api.legalActions(state)
        #get all state of ghosts
        ghosts = api.ghosts(state)
        #check if any ghost in my danger area(within 3 step to me)
        ghostlist = api.distanceLimited(ghosts, state, danger)

        # if there are ghosts in my danger area       
        if ghostlist:
            #Check directions of these ghost in the danger area
            #Remove all direction of these ghost in legal-move-directions of pacman

            for i in range(len(ghostlist)):
                    if ghostlist[i][1] > mystate[1] :
                       if Directions.NORTH in legal:
                               legal.remove(Directions.NORTH)
        
                    if ghostlist[i][1] < mystate[1] :
                            if Directions.SOUTH in legal:
                               legal.remove(Directions.SOUTH)
            
                    if ghostlist[i][0] < mystate[0] :
                            if Directions.WEST in legal:
                                legal.remove(Directions.WEST)
                
                    if ghostlist[i][0] > mystate[0]:
                            if Directions.EAST in legal:
                                legal.remove(Directions.EAST)
    

        #check if  pacman only have one direction can go
        # If it is, just go this direction.
        if len(legal) == 2 and Directions.STOP in legal:
            legal.remove(Directions.STOP)
            goto = random.choice(legal)

        # If pacman have more than one direction can go
        # let pacman make correct choice where pacman should go
        else:
            # if the direction of east is a wall and pacman go east,
            # but pacman will not move.
            # therefor the new utilitiy is same with the utilitiy of current(this) position
            if (self.map1.getValue(mystate[0]+1, mystate[1]) != '%'):
                myeast = self.map1.getValue(mystate[0]+1, mystate[1])
            else: myeast = myvalue

            if (self.map1.getValue(mystate[0]-1, mystate[1]) != '%'):
                mywest = self.map1.getValue(mystate[0]-1, mystate[1])
            else: mywest = myvalue

            if(self.map1.getValue(mystate[0], mystate[1]+1) != '%'):
                mynorth = self.map1.getValue(mystate[0], mystate[1]+1)
            else: mynorth = myvalue

            if(self.map1.getValue(mystate[0], mystate[1]-1) != '%'):
                mysouth = self.map1.getValue(mystate[0], mystate[1]-1)
            else: mysouth = myvalue

            #make a list to save all the payoff of legal directions
            mylist = []
            if Directions.EAST in legal:
                mylist.append(myeast)
            if Directions.SOUTH in legal:
                mylist.append(mysouth)
            if Directions.NORTH in legal:
                mylist.append(mynorth)
            if Directions.WEST in legal:
                mylist.append(mywest)
            #print "mylist",mylist

            #if no legal directions, ask pacman stay the same position
            if 	len(mylist) == 0:
                goto = Directions.STOP
            #find the max payoff is from which legal directions
            #ask pacman going the direction with biggest payoff
            elif max(mylist) == myeast and Directions.EAST in legal:
                goto = Directions.EAST
            elif max(mylist) == mysouth and Directions.SOUTH in legal:
                goto = Directions.SOUTH
            elif max(mylist) == mywest and Directions.WEST in legal:
                goto = Directions.WEST
            elif max(mylist) == mynorth and Directions.NORTH in legal:
                goto = Directions.NORTH
            # if pacman cannot make decision, just make a random choice
            else: goto = random.choice(api.legalActions(state))

        return api.makeMove(goto, api.legalActions(state))