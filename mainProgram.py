# Design standards:
#
# Constants are in ALL_CAPS with underscores to separate words
# Other variables/functions are in camelCase starting with a lowercase letter
# Classes are in CamelCase starting with a captial letter
# Give any construct a descriptive name to avoid duplicate names

import pygame, os, pickle, math, random, socket, time
import networkFunctions as nf
from pygame.locals import *

pygame.init()

WHITE  = (255, 255, 255)
YELLOW = (255, 255,   0)
BLACK  = (  0,   0,   0)

BORDER_WIDTH = 200
SCREEN_WIDTH = 550 + BORDER_WIDTH * 2
SCREEN_HEIGHT = 550
SCREEN_GRID_WIDTH = 11
SCREEN_GRID_HEIGHT = 11
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Treasure Hunters")

CLOCK = pygame.time.Clock()
FPS = 30
timePassed = CLOCK.tick(FPS) / 1000.0

condition = True

# key values
moveLeftKey = K_LEFT
moveRightKey = K_RIGHT
moveDownKey = K_DOWN
moveUpKey = K_UP
useToolKey = K_z
cycleToolLeftKey = K_a
cycleToolRightKey = K_s

# default game settings
# these can be changed in the options menu
biomesPerMap = 9 # MUST be equal a whole number squared at least 9
biomeLength = 11 # MUST be equal to 3+4n where n is a whole number >= 0

# main game variables
grid = [[]]
you = 0 # you the player
them = 0 # the other player
isMultiplayer = False
isHost = False # determines if you are server or client for multiplayer
currentName = 0
currentTool = 0
toolImage = 0
timeLimit = 180.0 # time limit in seconds
inventoryTimer = 0.0
toolTimer = 0.0 # the length of time the tool image is on screen for
toolInUse = False
gameTimer = 0.0

BIOMES = ["forest", "quarry", "farm", "arctic", "plains"]
TREASURE = ["diamond", "emerald", "ruby", "sapphire", "coin"]
NAMES = ["Anthony", "Caitlin", "Josh", "Matt"]
TOOLS = ["shovel", "axe", "pickaxe", "hammer", "scythe"]
MENU_OPTIONS = ["Single Player", "Multiplayer", "High Scores", "Settings", "Exit"]
OPTIONS = ["Host a game", "Join a game"]
PORT = 80

anthonyStartLocation = 0
caitlinStartLocation = 0
joshStartLocation = 0
mattStartLocation = 0

highScore1 = 0
highScore2 = 0
highScore3 = 0
highScore4 = 0
highScore5 = 0

# attempt to load high scores, catch error if pickle file hasn't been created
try:
    scoreFile = open("highScores", 'rb')
    highScore1 = pickle.load(scoreFile)
    highScore2 = pickle.load(scoreFile)
    highScore3 = pickle.load(scoreFile)
    highScore4 = pickle.load(scoreFile)
    highScore5 = pickle.load(scoreFile)
    scoreFile.close()
except IOError:
    pass

# attempt to load default settings, catch error if pickle file hasn't been created
try:
    settingsFile = open("settings", 'rb')
    biomesPerMap = pickle.load(settingsFile)
    biomeLength = pickle.load(settingsFile)
    settingsFile.close()
except IOError:
    pass

def saveHighScores():
    file = open("highScores", 'wb')
    pickle.dump(highScore1, file)
    pickle.dump(highScore2, file)
    pickle.dump(highScore3, file)
    pickle.dump(highScore4, file)
    pickle.dump(highScore5, file)
    file.close()

def saveSettings():
    file = open("settings", 'wb')
    pickle.dump(biomesPerMap, file)
    pickle.dump(biomeLength, file)
    file.close()

def getTreasureValueFromName(name):
    # returns the value of a treasure based on its name
    # these values have NOT been finalized
    
    if name == "diamond":
        return 1000
    elif name == "emerald":
        return 500
    elif name == "ruby":
        return 200
    elif name == "sapphire":
        return 100
    elif name == "coin":
        return 10
    else:
        return 0

def getToolFromPlayerName(name):
    # returns the default tool the given player starts with
    # the names and values have NOT been finalized

    if name == "Josh":
        return "pickaxe"
    elif name == "Anthony":
        return "axe"
    elif name == "Caitlin":
        return "scythe"
    else:
        return "hammer"

def getTerrainFromBiome(biome):
    # returns the terrain associated with the specified biome

    if biome == "forest":
        return "tree"
    elif biome == "quarry":
        return "rock"
    elif biome == "desert":
        return "rock"
    elif biome == "arctic":
        return "ice"
    elif biome == "plains":
        return "water"
    elif biome == "farm":
        return "wheat"

class Treasure(object):
    def __init__(self, name):
        self.name = name # the type of treasure it is
        self.value = getTreasureValueFromName(name) # the amount of money the treasure is worth
        self.image = pygame.image.load("images/treasure/" + name + ".png").convert()
        self.image.set_colorkey(WHITE) # makes white treasure background transparent

    def __str__(self):
        return self.name

class Terrain(object):
    def __init__(self, row, col, name, isSolid, treasure):
        self.row = row
        self.col = col
        self.name = name # the type of terrain it is (e.g. tree, rock, etc)
        self.isSolid = isSolid
        self.image = pygame.image.load("images/terrain/" + name + ".png")
        self.treasure = treasure # the gem included inside the terrain, if any
        self.isDestroyed = False # determines if terrain has been destroyed by a tool

    def __str__(self):
        return self.name
    
    def changeTerrain(self, name, isSolid):
        # changes terrain to a new terrain
        self.name = name
        self.image = pygame.image.load("images/terrain/" + name + ".png")
        self.isSolid = isSolid

    def changeTreasure(self, treasure):
        self.treasure = treasure
            
class Player(object):
    def __init__(self, row, col, speed, name):
        self.x = 250 + BORDER_WIDTH
        self.y = 250
        self.dispX = 0 # the amount of horizontal displacement the player experiences relative to the grid square
        self.dispY = 0 # the amount of vertical displacement the player experiences relative to the grid square
        self.row = row # the row the player is on on the grid
        self.col = col # the column the players is on on the grid
        self.speed = speed # the speed of the player (in pixels per second)
        self.movement = self.speed // FPS # the amount of pixels they move each frame
        self.diagonalMovement = int(self.movement * math.cos(45)) # the amount of pixels they move each frame diagonally
        self.direction = [] # keeps track of which direction(s) the player is moving in
        self.collisionGrid = [[0] * 3 for i in range(3)]
        self.updateCollisionGrid()
        self.name = name # the player"s name, used to determine many things
        self.orientation = "front"
        self.animationFrame = 1 # keeps track of which image to render in an animation
        self.image = pygame.image.load("images/characters/" + name + "/" + self.orientation + " " + str(self.animationFrame) + ".png")
        self.collisionSurface = pygame.surface.Surface((28, 34))
        self.money = 0 # the money the player has gained
        self.currentTool = getToolFromPlayerName(name) # the tool equipped by the player; initialized to their starting tool
        self.tools = [self.currentTool]
        self.toolAnimation = 0 # determines the animation frame of the tool being used
        self.hasBridge = False
        self.usingBridge = False

    def changeOrientation(self, orientation):
        self.orientation = orientation
    
    def changeImage(self):
        self.image = pygame.image.load("images/characters/" + self.name + "/" + self.orientation + " " + str(self.animationFrame) + ".png")
    
    def animate(self):
        if self.animationFrame < 10:
            self.animationFrame += 1
        else:
            self.animationFrame = 1
            
    def checkForCollisions(self):
        self.updateCollisionGrid()
        for i in self.collisionGrid:
            for j in i:
                if j.isSolid:
                    horizontalWrap = False
                    verticalWrap = False
                    leftX = self.col * 50 + self.dispX + 11
                    if leftX < 0:
                        leftX += 50 * biomeLength * int(math.sqrt(biomesPerMap))
                        horizontalWrap = True
                    rightX = leftX + self.collisionSurface.get_width() - 1
                    if rightX > 50 * biomeLength * int(math.sqrt(biomesPerMap)):
                        rightX -= 50 * biomeLength * int(math.sqrt(biomesPerMap))
                        horizontalWrap = True
                    upY = self.row * 50 + self.dispY + 8
                    if upY < 0:
                        upY += 50 * biomeLength * int(math.sqrt(biomesPerMap))
                        verticalWrap = True
                    downY = upY + self.collisionSurface.get_height() - 1
                    if downY > 50 * biomeLength * int(math.sqrt(biomesPerMap)):
                        downY -= 50 * biomeLength * int(math.sqrt(biomesPerMap))
                        verticalWrap = True
                    if (rightX >= j.col * 50 or rightX <= self.image.get_width() and horizontalWrap) and (leftX <= j.col * 50 + 50 or leftX > 50 * len(grid) - self.image.get_width() and horizontalWrap): # check if x's overlap
                        if (downY >= j.row * 50 or downY <= self.image.get_height() and verticalWrap) and (upY <= j.row * 50 + 50 or upY > 50 * len(grid) - self.image.get_height() and verticalWrap): # check if y's overlap
                            if horizontalWrap:
                                clipFromLeft = rightX
                                clipFromRight = 50 * biomeLength * int(math.sqrt(biomesPerMap)) - leftX
                            else:
                                clipFromLeft = rightX - j.col * 50 # the distance the player has clipped into the left side of the terrain
                                clipFromRight = j.col * 50 + 50 - leftX # the distance the player has clipped into the right side of the terrain
                            if verticalWrap:
                                clipFromAbove = downY
                                clipFromBelow = 50 * biomeLength * int(math.sqrt(biomesPerMap)) - upY
                            else:
                                clipFromAbove = downY - j.row * 50 # the distance the player had clipped into the upper side of the terrain
                                clipFromBelow = j.row * 50 + 50 - upY # the distance the player has clipped into the lower side of the terrain
                            
                            if clipFromLeft == min(clipFromLeft, clipFromRight, clipFromAbove, clipFromBelow):
                                self.dispX -= clipFromLeft - 1
                            elif clipFromRight == min(clipFromLeft, clipFromRight, clipFromAbove, clipFromBelow):
                                self.dispX += clipFromRight + 1
                            elif clipFromAbove == min(clipFromLeft, clipFromRight, clipFromAbove, clipFromBelow):
                                self.dispY -= clipFromAbove - 1
                            else:
                                self.dispY += clipFromBelow + 1
                elif j.isDestroyed and j.treasure != 0:
                    leftX = self.col * 50 + self.dispX + 11
                    rightX = leftX + self.collisionSurface.get_width()
                    upY = self.row * 50 + self.dispY + 8
                    downY = upY + self.collisionSurface.get_height()
                    if rightX > j.col * 50 and leftX < j.col * 50 + 50: # check if x's overlap
                        if downY > j.row * 50 and upY < j.row * 50 + 50: # check if y's overlap
                            # collided with treasure; collect it
                            if j.treasure.name == "bridge":
                                self.hasBridge = True
                            else:
                                self.money += j.treasure.value
                            j.treasure = 0
        if self.dispX >= 25:
            self.col += 1
            if self.col >= len(grid[0]):
                self.col = 0
            self.dispX -= 50
        elif self.dispX < -25:
            self.col -= 1
            if self.col < 0:
                self.col = len(grid[0]) - 1
            self.dispX += 50
        if self.dispY + 8 >= 25:
            self.row += 1
            if self.row >= len(grid):
                self.row = 0
            self.dispY -= 50
        elif self.dispY < -25:
            self.row -= 1
            if self.row < 0:
                self.row = len(grid) - 1
            self.dispY += 50
        self.updateCollisionGrid()
        updateScreenGrid()
                        
    def updateCollisionGrid(self):
        # call when the user has finished moving for the current frame.
        # updates the collision grid with the user"s grid position
        # and the grid square to their right, down, and down-right

        self.collisionGrid[0][0] = grid[self.row - 1][self.col - 1]
        self.collisionGrid[0][1] = grid[self.row - 1][self.col]
        self.collisionGrid[1][0] = grid[self.row][self.col - 1]
        self.collisionGrid[1][1] = grid[self.row][self.col]
        if self.col + 1 >= len(grid[0]):
            self.collisionGrid[0][2] = grid[self.row - 1][0]
            self.collisionGrid[1][2] = grid[self.row][0]
        else:
            self.collisionGrid[0][2] = grid[self.row - 1][self.col + 1]
            self.collisionGrid[1][2] = grid[self.row][self.col + 1]
        if self.row + 1 >= len(grid):
            self.collisionGrid[2][0] = grid[0][self.col - 1]
            self.collisionGrid[2][1] = grid[0][self.col]
            if self.col + 1 >= len(grid[0]):
                self.collisionGrid[2][2] = grid[0][0]
            else:
                self.collisionGrid[2][2] = grid[0][self.col + 1]
        else:
            self.collisionGrid[2][0] = grid[self.row + 1][self.col - 1]
            self.collisionGrid[2][1] = grid[self.row + 1][self.col]
            if self.col + 1 >= len(grid[0]):
                self.collisionGrid[2][2] = grid[self.row + 1][0]
            else:
                self.collisionGrid[2][2] = grid[self.row + 1][self.col + 1]
                
    def move(self):
        # moves player in the direction specified and animates them
        # if the direction is a compass direction, they move far
        # if the direction is a diagonal, they move less (picture unit circle)
        global toolInUse
        if toolInUse:
            if self.toolAnimation == 3:
                self.toolAnimation = 0
                toolInUse = False
            else:
                self.toolAnimation += 1
        if toolInUse == False:
            if "right" in self.direction and "down" in self.direction:
                self.dispX += self.diagonalMovement
                self.dispY += self.diagonalMovement
            elif "right" in self.direction and "up" in self.direction:
                self.dispX += self.diagonalMovement
                self.dispY -= self.diagonalMovement
            elif "right" in self.direction:
                self.dispX += self.movement
            elif "left" in self.direction and "down" in self.direction:
                self.dispX -= self.diagonalMovement
                self.dispY += self.diagonalMovement
            elif "left" in self.direction and "up" in self.direction:
                self.dispX -= self.diagonalMovement
                self.dispY -= self.diagonalMovement
            elif "left" in self.direction:
                self.dispX -= self.movement
            elif "down" in self.direction:
                self.dispY += self.movement
            elif "up" in self.direction:
                self.dispY -= self.movement

        if len(self.direction) > 0:
            self.animate()
        else:
            self.animationFrame = 1
        self.checkForCollisions()
        self.changeImage()


def createBiomeTreasure(numberOfTreasures):
    treasures = []
    count = 0
    # half of the terrain has no treasure
    for i in range(numberOfTreasures // 2):
        treasures.append(0)
        count += 1
    # quarter of the terrain has a coin
    for i in range(numberOfTreasures // 4):
        treasures.append(Treasure("coin"))
        count += 1
    # eighth of the terrain has a sapphire
    for i in range(numberOfTreasures // 8):
        treasures.append(Treasure("sapphire"))
        count += 1
    # two sixteenths of the terrain has a ruby or emerald
    for i in range(numberOfTreasures // 16):
        treasures.append(Treasure("ruby"))
        count += 1
        treasures.append(Treasure("emerald"))
        count += 1
    # last treasures are diamonds
    for i in range(count, numberOfTreasures):
        treasures.append(Treasure("diamond"))
    random.shuffle(treasures)
    return treasures

def getPairs(BPM, possibleExits):
    pairs = {}
    for i in range(BPM):
        # find pair to the right
        for j in range(possibleExits):
            if (i + 1) % math.sqrt(BPM) == 0:
                pair = (i, i - int(math.sqrt(BPM)) + 1, j)
            else:
                pair = (i, i + 1, j)
            pairs[pair] = ["right", None]
        # find pair to the left
        for j in range(possibleExits):
            if i % math.sqrt(BPM) == 0:
                pair = (i, i + int(math.sqrt(BPM)) - 1, j)
            else:
                pair = (i, i - 1, j)
            pairs[pair] = ["left", None]
        # find pair down
        for j in range(possibleExits):
            if BPM - math.sqrt(BPM) <= i and i < BPM:
                pair = (i, i - BPM + int(math.sqrt(BPM)), j)
            else:
                pair = (i, i + int(math.sqrt(BPM)), j)
            pairs[pair] = ["down", None]
        # find pair up
        for j in range(possibleExits):
            if 0 <= i and i < math.sqrt(BPM):
                pair = (i, i + BPM - int(math.sqrt(BPM)), j)
            else:
                pair = (i, i - int(math.sqrt(BPM)), j)
            pairs[pair] = ["up", None]
    return pairs

def determineBiomePaths(pairs, BPM, possibleExits):
    currentBiome = 0
    biomeHasExit = False
    for pair in sorted(pairs):
        if pair[0] != currentBiome:
            if biomeHasExit == False:
                pairs[lastPair][1] = True
                pairs[(lastPair[1], lastPair[0], lastPair[2])][1] = True
            currentBiome = pair[0]
            biomeHasExit = False
        if pairs[pair][1] == None:
            if random.randint(0, possibleExits) == 0:
                pairs[pair][1] = True
                pairs[(pair[1], pair[0], pair[2])][1] = True
                biomeHasExit = True
            else:
                pairs[pair][1] = False
                pairs[(pair[1], pair[0], pair[2])][1] = False
            lastPair = pair
    return pairs

def carveMaze(biome, defaultTerrain):
    # method to carve a maze out of a biome
    # uses a modified version of Kruskal's algorithm

    junctionSets = [] # keeps track of which parts of the maze are connected
    unconnectedEdges = []
    setCounter = 0 # keeps track of which value to add next to sets
    junctionsPerSide = len(biome) // 2

    # make all "junctions" in biome moveable and add them to a new set
    for i in range(1, len(biome) - 1, 2):
        for j in range(1, len(biome[0]) - 1):
            if i % 2 == 1 and j % 2 == 1:
                biome[i][j].changeTerrain(defaultTerrain, False)
                junctionSets.append({setCounter})
                setCounter += 1
            elif i % 2 == 1 and j % 2 == 0: # horizontal edge
                unconnectedEdges.append((setCounter - 1, setCounter, i, j))
        # add vertical edges if necessary
        if setCounter < junctionsPerSide * junctionsPerSide:
            for j in range(junctionsPerSide):
                unconnectedEdges.append((setCounter - junctionsPerSide + j, setCounter + j, i + 1, 1 + j * 2))

    # continue loop until all junctions have been connected
    while len(junctionSets) > 1:
        connected = False
        set1 = {}
        set2 = {}
        # select a random unconnected edge
        edge = random.choice(unconnectedEdges)
        unconnectedEdges.remove(edge)
        # check if junctions the edge touches are already connected
        for junction in junctionSets:
            if edge[0] in junction and edge[1] in junction:
                connected = True
                break;
            elif edge[0] in junction:
                set1 = junction
            elif edge[1] in junction:
                set2 = junction
        if connected == False:
            biome[edge[2]][edge[3]].changeTerrain(defaultTerrain, False)
            junctionSets.remove(set1)
            junctionSets.remove(set2)
            newJunction = set1.union(set2)
            junctionSets.append(newJunction)

    return biome

def generateRandomBiome(biomeName, tilesPerSide, possibleExits, BPM, paths, num):
    global anthonyStartLocation, caitlinStartLocation, joshStartLocation, mattStartLocation

    # generates all treasures for the biome
    treasures = createBiomeTreasure(tilesPerSide * tilesPerSide)

    defaultTerrain = ""
    if biomeName == "arctic":
        defaultTerrain = "snowy"
    elif biomeName == "farm":
        defaultTerrain == "farm ground"
    else:
        defaultTerrain = "ground"
    
    # initialize the biome as a 2D list of all 0s
    randomBiome = [[0] * tilesPerSide for i in range(tilesPerSide)]
    for i in range(tilesPerSide):
        for j in range(tilesPerSide):
            randomBiome[i][j] = Terrain(num // int(math.sqrt(BPM)) * tilesPerSide + i, num % int(math.sqrt(BPM)) * tilesPerSide + j, getTerrainFromBiome(biomeName), True, treasures.pop())
    
    # change all chosen exits to a moveable path
    for path in sorted(paths):
        if paths[path][1]:
            if paths[path][0] == "down":
                if possibleExits == 1:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2].changeTerrain(defaultTerrain, False)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 3].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide - 1][tilesPerSide * 2 // 3].changeTerrain(defaultTerrain, False)
                else: # defaults to 3
                    randomBiome[tilesPerSide - 1][tilesPerSide // 4].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide - 1][tilesPerSide * 3 // 4].changeTerrain(defaultTerrain, False)
            elif paths[path][0] == "up":
                if possibleExits == 1:
                    randomBiome[0][tilesPerSide // 2].changeTerrain(defaultTerrain, False)
                elif possibleExits == 2:
                    randomBiome[0][tilesPerSide // 3].changeTerrain(defaultTerrain, False)
                    randomBiome[0][tilesPerSide * 2 // 3].changeTerrain(defaultTerrain, False)
                else: # defaults to 3
                    randomBiome[0][tilesPerSide // 4].changeTerrain(defaultTerrain, False)
                    randomBiome[0][tilesPerSide // 2].changeTerrain(defaultTerrain, False)
                    randomBiome[0][tilesPerSide * 3 // 4].changeTerrain(defaultTerrain, False)
            elif paths[path][0] == "right":
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1].changeTerrain(defaultTerrain, False)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][tilesPerSide // 3].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide * 2 // 3][tilesPerSide - 1].changeTerrain(defaultTerrain, False)
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][tilesPerSide - 1].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide * 3 // 4][tilesPerSide - 1].changeTerrain(defaultTerrain, False)
            else: # defaults to left
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][0].changeTerrain(defaultTerrain, False)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][0].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide * 2 // 3][0].changeTerrain(defaultTerrain, False)
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][0].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide // 2][0].changeTerrain(defaultTerrain, False)
                    randomBiome[tilesPerSide * 3 // 4][0].changeTerrain(defaultTerrain, False)
    
    # carve the paths using the recursive backtracking algorithm
    carveMaze(randomBiome, defaultTerrain)

    return randomBiome

def generateRandomMap(biomesPerMap, tilesPerSide):
    # creates a pseudo-random map and all the treasures on it

    # initialize the map and a list of biomes
    randomMap = []
    generatedBiomes = []
    biomeTypes = []

    if biomesPerMap == 9:
        biomeTypes.append("forest")
        biomeTypes.append("forest")
        biomeTypes.append("quarry")
        biomeTypes.append("quarry")
        biomeTypes.append("arctic")
        biomeTypes.append("arctic")
        biomeTypes.append("farm")
        biomeTypes.append("farm")
        biomeTypes.append("plains")
    elif biomesPerMap == 16:
        for i in range(3):
            biomeTypes.append("forest")
        for i in range(3):
            biomeTypes.append("quarry")
        for i in range(3):
            biomeTypes.append("arctic")
        for i in range(3):
            biomeTypes.append("plains")
        for i in range(3):
            biomeTypes.append("farm")
    elif biomesPerMap == 25:
        for i in range(5):
            biomeTypes.append("forest")
        for i in range(5):
            biomeTypes.append("quarry")
        for i in range(5):
            biomeTypes.append("arctic")
        for i in range(5):
            biomeTypes.append("plains")
        for i in range(5):
            biomeTypes.append("farm")
    random.shuffle(biomeTypes)

    # determine number of exits from biome (default to 1)
    possibleExits = 1
    if tilesPerSide >= 99: # 3 possible exits
        possibleExits = 3
    elif tilesPerSide >= 63: # 2 possible exits
        possibleExits = 2

    # generate the biome paths (these determine where the biomes connect with each other
    biomePaths = determineBiomePaths(getPairs(biomesPerMap, possibleExits), biomesPerMap, possibleExits)
    # create biomes for the map
    for i in range(biomesPerMap):
        relevantPaths = {} # used to determine which paths affect the current biome
        # fill relevantPaths with all paths associated with the current biome
        for pair in sorted(biomePaths):
            if pair[0] == i:
                relevantPaths[pair] = biomePaths[pair]
        generatedBiomes.append(generateRandomBiome(biomeTypes[i], tilesPerSide, possibleExits, biomesPerMap, relevantPaths, i))
    
    for i in range(biomesPerMap):
        for j in range(len(generatedBiomes[i])):
            if i % int(math.sqrt(biomesPerMap)) == 0:
                randomMap.append(generatedBiomes[i][j])
            else:
                randomMap[i // int(math.sqrt(biomesPerMap)) * tilesPerSide + j] += generatedBiomes[i][j]

    # add a bridge as a treasure
    tile = random.choice(random.choice(randomMap))
    while tile.name == "water" or tile.treasure != 0:
        tile = random.choice(random.choice(randomMap))
    tile.changeTreasure(Treasure("bridge"))
    
    return randomMap

def setStartLocations():
    global anthonyStartLocation, caitlinStartLocation, joshStartLocation, mattStartLocation

    anthonyStartLocation = 0
    caitlinStartLocation = 0
    joshStartLocation = 0
    mattStartLocation = 0
    
    for i in range(int(math.sqrt(biomesPerMap))):
        for j in range(int(math.sqrt(biomesPerMap))):
            if grid[i * biomeLength][j * biomeLength].name == "tree" and anthonyStartLocation == 0:
                anthonyStartLocation = (i * biomeLength + biomeLength // 2, j * biomeLength + biomeLength // 2)
            elif grid[i * biomeLength][j * biomeLength].name == "wheat" and caitlinStartLocation == 0:
                caitlinStartLocation = (i * biomeLength + biomeLength // 2, j * biomeLength + biomeLength // 2)
            elif grid[i * biomeLength][j * biomeLength].name == "rock" and joshStartLocation == 0:
                joshStartLocation = (i * biomeLength + biomeLength // 2, j * biomeLength + biomeLength // 2)
            elif grid[i * biomeLength][j * biomeLength].name == "ice" and mattStartLocation == 0:
                mattStartLocation = (i * biomeLength + biomeLength // 2, j * biomeLength + biomeLength // 2)
                
# the main grid containing every piece of terrain and its location
grid = [[Terrain(0, 0, "ground", False, 0)] * biomeLength * int(math.sqrt(biomesPerMap))] * biomeLength * int(math.sqrt(biomesPerMap))
screenGrid = [[0] * 13 for i in range(13)]
you = Player(5, 5, 250, "Josh")

def updateScreenGrid():
    global screenGrid
    for i in range(13):
        for j in range(13):
            gridX = you.row - 6 + i
            if gridX >= biomeLength * int(math.sqrt(biomesPerMap)):
                gridX -= biomeLength * int(math.sqrt(biomesPerMap))
            elif gridX <= -biomeLength * int(math.sqrt(biomesPerMap)):
                gridX += biomeLength * int(math.sqrt(biomesPerMap))
            gridY = you.col - 6 + j
            if gridY >= biomeLength * int(math.sqrt(biomesPerMap)):
                gridY -= biomeLength * int(math.sqrt(biomesPerMap))
            elif gridY <= -biomeLength * int(math.sqrt(biomesPerMap)):
                gridY += biomeLength * int(math.sqrt(biomesPerMap))
            screenGrid[i][j] = grid[gridX][gridY]

updateScreenGrid()

def showInventory():
    global inventoryTimer
    while inventoryTimer > 0.0:
        shov = pygame.image.load("tools/shovel.png")
        ax = pygame.image.load("tools/axe.png")
        pickax = pygame.image.load("tools/pickaxe.png")
        hamm = pygame.image.load("tools/hammer.png")
        sick = pygame.image.load("tools/scythe.png")
        shov1 = pygame.image.load("tools/shovel 1.png")
        ax1 = pygame.image.load("tools/axe 1.png")
        pickax1 = pygame.image.load("tools/pickaxe 1.png")
        hamm1 = pygame.image.load("tools/hammer 1.png")
        sick1 = pygame.image.load("tools/scythe 1.png")
        for tool in TOOLS:
            if tool == "shovel" and tool == currentTool:
                SCREEN.blit(shov, (50, 500))
            elif tool == "shovel" and tool != currentTool:
                SCREEN.blit(shov1, (50, 500))
            elif tool == "axe" and tool == currentTool:
                SCREEN.blit(ax, (100, 500))
            elif tool == "axe" and tool != currentTool:
                SCREEN.blit(ax1, (100, 500))
            elif tool == "pickaxe" and tool == currentTool:
                SCREEN.blit(pickax, (150, 500))
            elif tool == "pickaxe" and tool != currentTool:
                SCREEN.blit(pickax1, (150, 500))
            elif tool == "hammer" and tool == currentTool:
                SCREEN.blit(hamm, (150, 500))
            elif tool == "hammer" and tool != currentTool:
                SCREEN.blit(hamm1, (150, 500))
            elif tool == "scythe" and tool == currentTool:
                SCREEN.blit(sick, (150, 500))
            elif tool == "scythe" and tool != currentTool:
                SCREEN.blit(sick1, (150, 500))
        ##pygame.display.update()

        
    if inventoryTimer < 0.0:
        inventoryTimer = 0
    ##pygame.display.update()
    
    ##CLOCK.tick(FPS)

def useTool(row, col):
    global toolInUse
    toolInUse = True
    if currentTool == "shovel":
        if grid[row][col].name == "ground":
            grid[row][col].changeTerrain("dug up grass", False)
            grid[row][col].isDestroyed = True
        elif grid[row][col].name == "snowy":
            grid[row][col].changeTerrain("dug up snow", False)
            grid[row][col].isDestroyed = True
        elif grid[row][col].name == "farm ground":
            grid[row][col].changeTerrain("dug up farm", False)
            grid[row][col].isDestroyed = True
    elif currentTool == "axe":
        if grid[row][col].name == "tree":
            grid[row][col].changeTerrain("tree stump", False)
            grid[row][col].isDestroyed = True
    elif currentTool == "pickaxe":
        if grid[row][col].name == "rock":
            grid[row][col].changeTerrain("crushed rock", False)
            grid[row][col].isDestroyed = True
    elif currentTool == "scythe":
        if grid[row][col].name == "wheat":
            grid[row][col].changeTerrain("sliced wheat", False)
            grid[row][col].isDestroyed = True
    elif currentTool == "hammer":
        if grid[row][col].name == "ice":
            grid[row][col].changeTerrain("crushed ice", False)
            grid[row][col].isDestroyed = True

def handleGameEvents():
    global condition, currentTool, toolImage, toolTimer
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            os._exit(1)
        elif event.type == KEYDOWN:
            if event.key == moveLeftKey:
                if len(you.direction) == 0:
                    you.changeOrientation("left")
                if "left" not in you.direction:
                    you.direction.append("left")
            elif event.key == moveRightKey:
                if len(you.direction) == 0:
                    you.changeOrientation("right")
                if "right" not in you.direction:
                    you.direction.append("right")
            elif event.key == moveDownKey:
                if len(you.direction) == 0:
                    you.changeOrientation("front")
                if "down" not in you.direction:
                    you.direction.append("down")
            elif event.key == moveUpKey:
                if len(you.direction) == 0:
                    you.changeOrientation("back")
                if "up" not in you.direction:
                    you.direction.append("up")
            elif event.key == useToolKey:
                if you.orientation == "right": # facing right
                    if you.col == len(grid[0]) - 1: # check if user is at rightmost edge of map, if so, prevent IndexError
                        useTool(you.row, 0)
                    else:
                        useTool(you.row, you.col + 1)
                elif you.orientation == "left": # facing left
                    useTool(you.row, you.col - 1)
                elif you.orientation == "front": # facing down
                    if you.row == len(grid) - 1: # check if user is at downmost edge of map, if so, prevent IndexError
                        useTool(0, you.col)
                    else:
                        useTool(you.row + 1, you.col)
                elif you.orientation == "back": # facing up
                    useTool(you.row - 1, you.col)
            elif event.key == cycleToolLeftKey:
                currentTool = TOOLS[TOOLS.index(currentTool) - 1]
                toolImage = pygame.image.load("images/tools/" + currentTool + ".png")
                toolTimer = 0.5
                inventoryTimer = 2.0
            elif event.key == cycleToolRightKey:
                if TOOLS.index(currentTool) == len(TOOLS) - 1:
                    currentTool = TOOLS[0]
                else:
                    currentTool = TOOLS[TOOLS.index(currentTool) + 1]
                toolImage = pygame.image.load("images/tools/" + currentTool + ".png")
                toolTimer = 0.5
                inventoryTimer = 2.0
        elif event.type == KEYUP:
            if event.key == moveLeftKey:
                if "left" in you.direction:
                    you.direction.remove("left")
                if "down" in you.direction:
                    you.changeOrientation("front")
                elif "up" in you.direction:
                    you.changeOrientation("back")
                elif "right" in you.direction:
                    you.changeOrientation("right")
            elif event.key == moveRightKey:
                if "right" in you.direction:
                    you.direction.remove("right")
                if "down" in you.direction:
                    you.changeOrientation("front")
                elif "up" in you.direction:
                    you.changeOrientation("back")
                elif "left" in you.direction:
                    you.changeOrientation("left")
            elif event.key == moveDownKey:
                if "down" in you.direction:
                    you.direction.remove("down")
                if "left" in you.direction:
                    you.changeOrientation("left")
                elif "right" in you.direction:
                    you.changeOrientation("right")
                elif "up" in you.direction:
                    you.direction.remove("up")
            elif event.key == moveUpKey:
                if "up" in you.direction:
                    you.direction.remove("up")
                if "left" in you.direction:
                    you.changeOrientation("left")
                elif "right" in you.direction:
                    you.changeOrientation("right")
                elif "down" in you.direction:
                    you.changeOrientation("front")

def characterSelection(hostCharacter):
    global condition, currentName
    currentName = 0
    condition = True
    characterText = font.render("Select a character", True, YELLOW, BLACK)
    anthonyText = font.render("Anthony", True, YELLOW, BLACK)
    caitlinText = font.render("Caitlin", True, YELLOW, BLACK)
    joshText = font.render("Josh", True, YELLOW, BLACK)
    mattText = font.render("Matt", True, YELLOW, BLACK)
    yellowCursor = pygame.image.load("images/yellow cursor.png").convert()
    characterText.set_colorkey(BLACK)
    anthonyText.set_colorkey(BLACK)
    caitlinText.set_colorkey(BLACK)
    joshText.set_colorkey(BLACK)
    mattText.set_colorkey(BLACK)
    yellowCursor.set_colorkey(BLACK)
    while condition:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                os._exit(0)
            elif event.type == KEYDOWN:
                if event.key == moveUpKey:
                    if currentName == 0:
                        currentName = 3
                    else:
                        currentName -= 1
                elif event.key == moveDownKey:
                    if currentName == 3:
                        currentName = 0
                    else:
                        currentName += 1
                elif event.key == useToolKey:
                    ##TODO: give error to client when trying to choose host's chosen character
                    if NAMES[currentName] != hostCharacter:
                        condition = False
        SCREEN.fill(BLACK)
        SCREEN.blit(title, (BORDER_WIDTH, 0))
        SCREEN.blit(characterText, (SCREEN_WIDTH // 2 - characterText.get_width() // 2, 250))
        SCREEN.blit(anthonyText, (SCREEN_WIDTH // 2 - anthonyText.get_width() // 2, 300))
        SCREEN.blit(caitlinText, (SCREEN_WIDTH // 2 - caitlinText.get_width() // 2, 350))
        SCREEN.blit(joshText, (SCREEN_WIDTH // 2 - joshText.get_width() // 2, 400))
        SCREEN.blit(mattText, (SCREEN_WIDTH // 2 - mattText.get_width() // 2, 450))
        SCREEN.blit(yellowCursor, (BORDER_WIDTH + 100, 300 + 50 * currentName))
        pygame.display.update()
        CLOCK.tick(FPS)
        
    return NAMES[currentName]

def mapStartUp(): 
    global biomesPerMap, biomeLength, condition, currentName, currentTool, gameTimer, grid, you
    condition = True
    generateText = font.render("Generating map; this may take a while...", True, YELLOW, BLACK)
    generateText.set_colorkey(BLACK)
    SCREEN.fill(BLACK)
    SCREEN.blit(title, (BORDER_WIDTH, 0))
    SCREEN.blit(generateText, (SCREEN_WIDTH // 2 - generateText.get_width() // 2, 350))
    pygame.display.update()
    CLOCK.tick(FPS)
    if isHost:
        grid = generateRandomMap(biomesPerMap, biomeLength)
    setStartLocations()
    if currentName == 0:
        you = Player(anthonyStartLocation[0], anthonyStartLocation[1], 250, NAMES[currentName].lower())
    elif currentName == 1:
        you = Player(caitlinStartLocation[0], caitlinStartLocation[1], 250, NAMES[currentName].lower())
    elif currentName == 2:
        you = Player(joshStartLocation[0], joshStartLocation[1], 250, NAMES[currentName].lower())
    else:
        you = Player(mattStartLocation[0], mattStartLocation[1], 250, NAMES[currentName].lower())
    currentTool = getToolFromPlayerName(NAMES[currentName])
    you.checkForCollisions()
    gameTimer = timeLimit
    isMultiplayer = False

def gameStartUp():
    global condition
    global highScore1, highScore2, highScore3, highScore4, highScore5

    while condition:
        executeGameFrame()

    timeUp = font.render("Time up!", True, WHITE, BLACK)
    timeUp.set_colorkey(BLACK)
    timeUpTimer = 2.0
    while timeUpTimer > 0.0:
        SCREEN.blit(timeUp, (SCREEN_WIDTH // 2 - timeUp.get_width() // 2, 100))
        pygame.display.update()
        CLOCK.tick(FPS)
        timeUpTimer -= timePassed
    scoreText = font.render("Your score: $" + str(you.money), True, WHITE, BLACK)
    nextText = font.render("", True, WHITE, BLACK)
    quitText = font.render("Press any key to go back to the main menu.", True, WHITE, BLACK)
    if you.money > highScore1:
        nextText = font.render("You broke the highest score!", True, WHITE, BLACK)
        highScore5 = highScore4
        highScore4 = highScore3
        highScore3 = highScore2
        highScore2 = highScore1
        highScore1 = you.money
    elif you.money > highScore2:
        nextText = font.render("You broke the second highest score!", True, WHITE, BLACK)
        highScore5 = highScore4
        highScore4 = highScore3
        highScore3 = highScore2
        highScore2 = you.money
    elif you.money > highScore3:
        nextText = font.render("You broke the third highest score!", True, WHITE, BLACK)
        highScore5 = highScore4
        highScore4 = highScore3
        highScore3 = you.money
    elif you.money > highScore4:
        nextText = font.render("You broke the fourth highest score!", True, WHITE, BLACK)
        highScore5 = highScore4
        highScore4 = you.money
    elif you.money > highScore5:
        nextText = font.render("You broke the fifth highest score!", True, WHITE, BLACK)
        highScore5 = you.money
    saveHighScores()
    waitTimer = 1.0
    condition = True
    while condition:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                os._exit(0)
            elif event.type == KEYDOWN:
                if waitTimer <= 0.0:
                    condition = False
        SCREEN.fill(BLACK)
        SCREEN.blit(scoreText, (SCREEN_WIDTH // 2 - scoreText.get_width() // 2, 200))
        SCREEN.blit(nextText, (SCREEN_WIDTH // 2 - nextText.get_width() // 2, 250))
        if waitTimer <= 0.0:
            SCREEN.blit(quitText, (SCREEN_WIDTH // 2 - quitText.get_width() // 2, 300))
        pygame.display.update()
        CLOCK.tick(FPS)
        waitTimer -= timePassed
        if waitTimer < 0.0:
            waitTimer = 0.0

def executeGameFrame():
    global gameTimer, toolTimer, inventoryTimer, condition
    handleGameEvents()
    if isMultiplayer:
        # server sends key inputs
        # client reads server key inputs
        # client sends key inputs
        # server reads client key inputs

        # other player moves
        pass
    if "left" in you.direction and "right" in you.direction:
        you.direction.remove("left")
        you.direction.remove("right")
    if "down" in you.direction and "up" in you.direction:
        you.direction.remove("down")
        you.direction.remove("up")
    you.move()
    # render new frame: fill screen with solid color, blit the grid, and then blit the player
    SCREEN.fill(BLACK)
    for i in range(len(screenGrid)):
        for j in range(len(screenGrid[0])):
            SCREEN.blit(screenGrid[i][j].image, (50 * (j - 1) - you.dispX + BORDER_WIDTH, 50 * (i - 1) - you.dispY))
            if screenGrid[i][j].isDestroyed and screenGrid[i][j].treasure != 0:
                SCREEN.blit(screenGrid[i][j].treasure.image, (50 * (j - 1) - you.dispX + BORDER_WIDTH, 50 * (i - 1) - you.dispY))
    if toolInUse:
        toolAnimation = pygame.image.load("images/tools/" + currentTool + " " + you.orientation + " " + str(you.toolAnimation) + ".png").convert()
        toolAnimation.set_colorkey(WHITE)
        if you.orientation == "right":
            SCREEN.blit(toolAnimation, (you.x + 30, you.y + 12))
        elif you.orientation == "left":
            SCREEN.blit(toolAnimation, (you.x - 15, you.y + 12))
        elif you.orientation == "front":
            SCREEN.blit(toolAnimation, (you.x + 8, you.y + 30))
        else:
            SCREEN.blit(toolAnimation, (you.x + 8, you.y - 15))
    SCREEN.blit(you.image, (you.x, you.y))
    if isMultiplayer:
        # blit other player to screen if they are on screen
        pass
    if toolTimer > 0.0:
        SCREEN.blit(toolImage, (you.x + 5, you.y - 45))
    pygame.draw.rect(SCREEN, BLACK, (0, 0, BORDER_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(SCREEN, BLACK, (SCREEN_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, SCREEN_HEIGHT))
    minutesLeft = int(gameTimer) // 60
    secondsLeft = int(gameTimer) - 60 * (int(gameTimer) // 60)
    if secondsLeft < 10:
        timeLeft = str(minutesLeft) + ":0" + str(secondsLeft)
    else:
        timeLeft = str(minutesLeft) + ":" + str(secondsLeft)
    timerImage = font.render(timeLeft, True, WHITE, BLACK)
    moneyImage = font.render("$" + str(you.money), True, WHITE, BLACK)
    SCREEN.blit(timerImage, (0, 0))
    SCREEN.blit(moneyImage, (0, SCREEN_HEIGHT // 2))
    toolTimer -= timePassed
    if toolTimer < 0.0:
        toolTimer = 0.0
    if inventoryTimer > 0.0:
        showInventory()
    if inventoryTimer < 0.0:
        inventoryTimer = 0.0
    pygame.display.update()
    CLOCK.tick(FPS)
    gameTimer -= timePassed
    if gameTimer <= 0.0:
        condition = False

title = pygame.image.load("images/Title Card.png")
font = pygame.font.SysFont("helvetica", 32)

while True:
    gameSelection = True
    selection = 0
    singlePlayerText = font.render("Single Player", True, YELLOW, BLACK)
    multiplayerText = font.render("Multiplayer", True, YELLOW, BLACK)
    highScoresText = font.render("High Scores", True, YELLOW, BLACK)
    settingsText = font.render("Settings", True, YELLOW, BLACK)
    exitText = font.render("Exit", True, YELLOW, BLACK)
    yellowCursor = pygame.image.load("images/yellow cursor.png").convert()
    singlePlayerText.set_colorkey(BLACK)
    multiplayerText.set_colorkey(BLACK)
    highScoresText.set_colorkey(BLACK)
    settingsText.set_colorkey(BLACK)
    exitText.set_colorkey(BLACK)
    yellowCursor.set_colorkey(BLACK)
    while gameSelection:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                os._exit(0)
            elif event.type == KEYDOWN:
                if event.key == moveDownKey:
                    if selection == len(MENU_OPTIONS) - 1:
                        selection = 0
                    else:
                        selection += 1
                elif event.key == moveUpKey:
                    if selection == 0:
                        selection = len(MENU_OPTIONS) - 1
                    else:
                        selection -= 1
                elif event.key == useToolKey:
                    gameSelection = False
        SCREEN.fill(BLACK)
        SCREEN.blit(title, (BORDER_WIDTH, 0))
        SCREEN.blit(singlePlayerText, (SCREEN_WIDTH // 2 - singlePlayerText.get_width() // 2, 250))
        SCREEN.blit(multiplayerText, (SCREEN_WIDTH // 2 - multiplayerText.get_width() // 2, 300))
        SCREEN.blit(highScoresText, (SCREEN_WIDTH // 2 - highScoresText.get_width() // 2, 350))
        SCREEN.blit(settingsText, (SCREEN_WIDTH // 2 - settingsText.get_width() // 2, 400))
        SCREEN.blit(exitText, (SCREEN_WIDTH // 2 - exitText.get_width() // 2, 450))
        SCREEN.blit(yellowCursor, (BORDER_WIDTH + 100, 250 + 50 * selection))
        pygame.display.update()
        CLOCK.tick(FPS)

    if selection == 0: # single player
        isMultiplayer = False
        isHost = True
        chosenCharacter = characterSelection("none")
        mapStartUp()
        gameStartUp()

    elif selection == 1: # multiplayer
        selection = 0
        condition = True
        mainText = font.render("Host a game or join a game?", True, YELLOW, BLACK)
        hostText = font.render(OPTIONS[0], True, YELLOW, BLACK)
        joinText = font.render(OPTIONS[1], True, YELLOW, BLACK)
        backText = font.render("Back", True, YELLOW, BLACK)
        mainText.set_colorkey(BLACK)
        hostText.set_colorkey(BLACK)
        joinText.set_colorkey(BLACK)
        backText.set_colorkey(BLACK)
        while condition:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    os._exit(0)
                elif event.type == KEYDOWN:
                    if event.key == moveDownKey:
                        if selection == 2:
                            selection = 0
                        else:
                            selection += 1
                    elif event.key == moveUpKey:
                        if selection == 0:
                            selection = 2
                        else:
                            selection -= 1
                    elif event.key == useToolKey:
                        condition = False
            SCREEN.blit(title, (BORDER_WIDTH, 0))
            SCREEN.blit(mainText, (SCREEN_WIDTH // 2 - mainText.get_width() // 2, 300))
            SCREEN.blit(hostText, (SCREEN_WIDTH // 2 - hostText.get_width() // 2, 350))
            SCREEN.blit(joinText, (SCREEN_WIDTH // 2 - joinText.get_width() // 2, 400))
            SCREEN.blit(backText, (SCREEN_WIDTH // 2 - backText.get_width() // 2, 450))
            SCREEN.blit(yellowCursor, (BORDER_WIDTH + 100, 350 + 50 * selection))
            pygame.display.update()
            CLOCK.tick(FPS)
           
            if selection == 0:
                #Start server
                IPAddr = nf.fGetIP()
                SCREEN.blit(title, (BORDER_WIDTH, 0))
                fontObj = font.render(("Your IP is: " + IPAddr), True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                pygame.display.update()
                CLOCK.tick(FPS)
                serverSocket = nf.fCreateServer(PORT)
                isHost = True

                flag = True
                while flag:
                    try:
                        serverSocket.settimeout(35) # Time server waits for client to connect
                        serverConnection = nf.fCreateConnection(serverSocket)
                    except socket.timeout:
                        SCREEN.blit(title, (BORDER_WIDTH, 0))
                        fontObj = font.render("Client failed to connect.", True, YELLOW, BLACK)
                        fontObj.set_colorkey(BLACK)
                        SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                        pygame.display.update()
                        CLOCK.tick(FPS)
                        time.sleep(5)
                        nf.fCloseServer(serverSocket)
                        pygame.quit()
                        os._exit(0)
                        break
                    except:
                        raise
                    else:
                        SCREEN.blit(title, (BORDER_WIDTH, 0))
                        fontObj = font.render("Client connected.", True, YELLOW, BLACK)
                        fontObj.set_colorkey(BLACK)
                        SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                        pygame.display.update()
                        CLOCK.tick(FPS)

                        serverConnection.setblocking(1)
                        nf.fSendToClient(serverConnection, "connected")
                        isMultiplayer = True
                        
                        #Choose character and tell client
                        chosenCharacter = characterSelection("none")
                        nf.fSendToClient(serverConnection, chosenCharacter)

                        #Create map and send to client
                        mapStartUp()
         
                        #Sending grid to client
                        nf.fSendMapToClient(serverConnection, grid)

                        #Checking that client is ready
                        clientStatus = nf.fReceiveFromClient(serverConnection)

                        #If client is ready, start game
                        if clientStatus == "ready":
                            SCREEN.blit(title, (BORDER_WIDTH, 0))
                            fontObj = font.render("Starting game...", True, YELLOW, BLACK)
                            fontObj.set_colorkey(BLACK)
                            SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                            pygame.display.update()
                            CLOCK.tick(FPS)
                            time.sleep(2)
                            gameStartUp()

                        #time.sleep(5)
                        #nf.fCloseServer(serverSocket) #this is for debugging
                        #pygame.quit()
                        #os._exit(0)
                        
                        #send/receive here
                        flag = False
                        
            elif selection == 1:
                #Start client
                isHost = False
                SCREEN.blit(title, (BORDER_WIDTH, 0))
                fontObj = font.render("What is the host's IP?", True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                pygame.display.update()
                CLOCK.tick(FPS)

                pygame.draw.rect(SCREEN, BLACK, (100, 450, 345, 35))
                pygame.display.update()
                CLOCK.tick(FPS)
                ipString = []
                while True:
                    while True:
                        event = pygame.event.poll()
                        if event.type == KEYDOWN:
                            inkey = event.key
                            break
                        elif event.type == QUIT:
                            pygame.quit()
                            os._exit(0)
                        else:
                            pass
                    if inkey == K_BACKSPACE:
                        ipString = ipString[0:-1]
                    elif inkey == K_RETURN:
                        break
                    elif inkey <= 127:
                        ipString.append(chr(inkey))
                    ipStr = ''.join(ipString)
                    fontObj2 = font.render(ipStr, True, YELLOW, BLACK)
                    fontObj2.set_colorkey(BLACK)
                    pygame.draw.rect(SCREEN, BLACK, (100, 450, 350, 35)) 
                    SCREEN.blit(fontObj2, (SCREEN_WIDTH // 2 - fontObj2.get_width() // 2, 450))
                    pygame.display.update()
                    CLOCK.tick(FPS)

                clientSocket = nf.fCreateClient(ipStr, PORT)
                SCREEN.blit(title, (BORDER_WIDTH, 0))
                fontObj = font.render("Connecting...", True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                pygame.display.update()
                CLOCK.tick(FPS)

                data = nf.fReceiveFromServer(clientSocket)
                if data == "connected":
                    SCREEN.blit(title, (BORDER_WIDTH, 0))
                    fontObj = font.render("Successfully connected.", True, YELLOW, BLACK)
                    fontObj.set_colorkey(BLACK)
                    SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                    pygame.display.update()
                    CLOCK.tick(FPS)
                    isMultiplayer = True

                time.sleep(2)
                #Receive host's chosen character
                SCREEN.blit(title, (BORDER_WIDTH, 0))
                fontObj = font.render("Host is choosing character", True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                pygame.display.update()
                CLOCK.tick(FPS)

                hostCharacter = nf.fReceiveFromServer(clientSocket)
                
                #Client chooses character different from host's
                chosenCharacter = characterSelection(hostCharacter)

                #Receive grid
                SCREEN.blit(title, (BORDER_WIDTH, 0))
                fontObj = font.render("Receiving map from server", True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                pygame.display.update()
                CLOCK.tick(FPS)
                grid = nf.fReceiveMapFromServer(clientSocket)

                #isHost being set to False will prevent a new grid from being created
                mapStartUp()
                
                #Tell server that client is ready
                nf.fSendToServer(clientSocket, "ready")

                SCREEN.blit(title, (BORDER_WIDTH, 0))
                fontObj = font.render("Starting game...", True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                pygame.display.update()
                CLOCK.tick(FPS)
                time.sleep(2)
                gameStartUp()
                
                 
                #nf.fCloseClient(clientSocket)  #this is for debugging
                #time.sleep(5)
                #pygame.quit()
                #os._exit(0)
                
    elif selection == 2: # high scores
        scoreImage1 = font.render("1: $" + str(highScore1), True, WHITE, BLACK)
        scoreImage2 = font.render("2: $" + str(highScore2), True, WHITE, BLACK)
        scoreImage3 = font.render("3: $" + str(highScore3), True, WHITE, BLACK)
        scoreImage4 = font.render("4: $" + str(highScore4), True, WHITE, BLACK)
        scoreImage5 = font.render("5: $" + str(highScore5), True, WHITE, BLACK)
        condition = True
        while condition:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    os._exit(0)
                elif event.type == KEYDOWN:
                    condition = False
                elif event.type == MOUSEBUTTONDOWN:
                    condition = False
            SCREEN.fill(BLACK)
            SCREEN.blit(scoreImage1, (150 + BORDER_WIDTH, 150))
            SCREEN.blit(scoreImage2, (150 + BORDER_WIDTH, 200))
            SCREEN.blit(scoreImage3, (150 + BORDER_WIDTH, 250))
            SCREEN.blit(scoreImage4, (150 + BORDER_WIDTH, 300))
            SCREEN.blit(scoreImage5, (150 + BORDER_WIDTH, 350))
            pygame.display.update()
            CLOCK.tick(FPS)
    elif selection == 3: # settings
        exitText = font.render("Back to menu", True, WHITE, BLACK)
        cursor = pygame.image.load("images/cursor.png")
        currentSelection = 0
        condition = True
        while condition:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    os._exit(0)
                elif event.type == KEYDOWN:
                    if event.key == moveRightKey:
                        if currentSelection == 0:
                            if biomesPerMap == 9:
                                biomesPerMap = 16
                            elif biomesPerMap == 16:
                                biomesPerMap = 25
                        elif currentSelection == 1:
                            if biomeLength < 59:
                                biomeLength += 12
                    elif event.key == moveLeftKey:
                        if currentSelection == 0:
                            if biomesPerMap == 25:
                                biomesPerMap = 16
                            elif biomesPerMap == 16:
                                biomesPerMap = 9
                        elif currentSelection == 1:
                            if biomeLength > 11:
                                biomeLength -= 12
                    elif event.key == moveDownKey:
                        if currentSelection < 2:
                            currentSelection += 1
                    elif event.key == moveUpKey:
                        if currentSelection > 0:
                            currentSelection -= 1
                    elif event.key == useToolKey:
                        if currentSelection == 2:
                            condition = False
            
            biomeNumText = font.render("Number of Biomes: " + str(biomesPerMap), True, WHITE, BLACK)
            biomeSizeText = font.render("Biome Side Length: " + str(biomeLength), True, WHITE, BLACK)
            SCREEN.fill(BLACK)
            SCREEN.blit(biomeNumText, (150 + BORDER_WIDTH, 150))
            SCREEN.blit(biomeSizeText, (150 + BORDER_WIDTH, 200))
            SCREEN.blit(exitText, (150 + BORDER_WIDTH, 250))
            if currentSelection == 0:
                SCREEN.blit(cursor, (50 + BORDER_WIDTH, 150))
            elif currentSelection == 1:
                SCREEN.blit(cursor, (50 + BORDER_WIDTH, 200))
            elif currentSelection == 2:
                SCREEN.blit(cursor, (50 + BORDER_WIDTH, 250))
            pygame.display.update()
            CLOCK.tick(FPS)
        saveSettings()
    elif selection == 4: # exit
        pygame.quit()
        os._exit(0)
