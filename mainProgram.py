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

SCREEN_WIDTH = 550
SCREEN_HEIGHT = 550
SCREEN_GRID_WIDTH = 11
SCREEN_GRID_HEIGHT = 11
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Treasure Hunters")

CLOCK = pygame.time.Clock()
FPS = 30
timePassed = CLOCK.tick(FPS) / 1000.0

condition = True

# default key values
# these can be changed in the options menu
moveLeftKey = K_LEFT
moveRightKey = K_RIGHT
moveDownKey = K_DOWN
moveUpKey = K_UP
useToolKey = K_z
cycleToolLeftKey = K_a
cycleToolRightKey = K_s

# default game settings
# these can be changed in the options menu
timeLimit = 300.0 # time limit in seconds
biomesPerMap = 9 # MUST be equal a whole number squared at least 9
biomeLength = 11 # MUST be equal to 3+4n where n is a whole number >= 0

# main game variables
grid = [[]]
you = 0
currentName = 0
currentTool = 0
toolImage = 0
inventoryTimer = 0.0
toolTimer = 0.0 # the length of time the tool image is on screen for

printDebug = False

BIOMES = ["forest", "quarry", "desert", "arctic", "plains"]
TREASURE = ["diamond", "emerald", "ruby", "sapphire", "coin"]
NAMES = ["Anthony", "Caitlin", "Josh", "Matt"]
TOOLS = ["shovel", "axe", "pickaxe"]
MENU_OPTIONS = ["Single Player", "Multiplayer"]
OPTIONS = ["Host a game", "Join a game"]
PORT = 80

highScore1 = 0
highScore2 = 0
highScore3 = 0
highScore4 = 0
highScore5 = 0

# attempt to load high scores, catch error if pickle file hasn't been created
try:
    scoreFile = open("highScores", "rb")
    highScore1 = pickle.load(scoreFile)
    highScore2 = pickle.load(scoreFile)
    highScore3 = pickle.load(scoreFile)
    highScore4 = pickle.load(scoreFile)
    highScore5 = pickle.load(scoreFile)
    scoreFile.close()
except IOError:
    pass

def saveHighScores():
    file = open("highScores", "wb")
    pickle.dump(file, highScore1)
    pickle.dump(file, highScore2)
    pickle.dump(file, highScore3)
    pickle.dump(file, highScore4)
    pickle.dump(file, highScore5)
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
        return "shovel"
    elif name == "Anthony":
        return "axe"
    elif name == "Caitlin":
        return "pickaxe"
    else:
        return "sword"

def getTerrainFromBiome(biome):
    # returns the terrain associated with the specified biome

    if biome == "forest":
        return "tree"
    elif biome == "quarry":
        return "rock"
    elif biome == "desert":
        return "rock"
    elif biome == "arctic":
        return "snowy"
    elif biome == "plains":
        return "water"

class Treasure(object):
    def __init__(self, name):
        self.name = name # the type of treasure it is
        self.value = getTreasureValueFromName(name) # the amount of money the treasure is worth
        self.image = pygame.image.load("images/treasure/" + name + ".png").convert()
        self.image.set_colorkey(WHITE) # makes white treasure background transparent

class Terrain(object):
    def __init__(self, row, col, name, isSolid, treasure):
        self.row = row
        self.col = col
        self.name = name # the type of terrain it is (e.g. tree, rock, etc)
        self.isSolid = isSolid
        self.image = pygame.image.load("images/terrain/" + name + ".png")
        self.treasure = treasure # the gem included inside the terrain, if any
        self.isDestroyed = False # determines if terrain has been destroyed by a tool
    
    def changeTerrain(self, name, isSolid):
        # changes terrain to a new terrain
        self.name = name
        self.image = pygame.image.load("images/terrain/" + name + ".png")
        self.isSolid = isSolid

    def changeTreasure(self, treasure):
        self.treasure = treasure
            
class Player(object):
    def __init__(self, row, col, speed, name):
        self.x = 250
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

def carveMaze(biome):
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
                biome[i][j].changeTerrain("ground", False)
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
            biome[edge[2]][edge[3]].changeTerrain("ground", False)
            junctionSets.remove(set1)
            junctionSets.remove(set2)
            newJunction = set1.union(set2)
            junctionSets.append(newJunction)

    return biome

def generateRandomBiome(tilesPerSide, possibleExits, BPM, paths, num):
    # generates a random biome that is a part of the world map (e.g. forest)
    biomeName = random.choice(BIOMES)

    # generates all treasures for the biome
    treasures = createBiomeTreasure(tilesPerSide * tilesPerSide)
    
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
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2].changeTerrain("ground", False)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 3].changeTerrain("ground", False)
                    randomBiome[tilesPerSide - 1][tilesPerSide * 2 // 3].changeTerrain("ground", False)
                else: # defaults to 3
                    randomBiome[tilesPerSide - 1][tilesPerSide // 4].changeTerrain("ground", False)
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2].changeTerrain("ground", False)
                    randomBiome[tilesPerSide - 1][tilesPerSide * 3 // 4].changeTerrain("ground", False)
            elif paths[path][0] == "up":
                if possibleExits == 1:
                    randomBiome[0][tilesPerSide // 2].changeTerrain("ground", False)
                elif possibleExits == 2:
                    randomBiome[0][tilesPerSide // 3].changeTerrain("ground", False)
                    randomBiome[0][tilesPerSide * 2 // 3].changeTerrain("ground", False)
                else: # defaults to 3
                    randomBiome[0][tilesPerSide // 4].changeTerrain("ground", False)
                    randomBiome[0][tilesPerSide // 2].changeTerrain("ground", False)
                    randomBiome[0][tilesPerSide * 3 // 4].changeTerrain("ground", False)
            elif paths[path][0] == "right":
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1].changeTerrain("ground", False)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][tilesPerSide // 3].changeTerrain("ground", False)
                    randomBiome[tilesPerSide * 2 // 3][tilesPerSide - 1].changeTerrain("ground", False)
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][tilesPerSide - 1].changeTerrain("ground", False)
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1].changeTerrain("ground", False)
                    randomBiome[tilesPerSide * 3 // 4][tilesPerSide - 1].changeTerrain("ground", False)
            else: # defaults to left
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][0].changeTerrain("ground", False)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][0].changeTerrain("ground", False)
                    randomBiome[tilesPerSide * 2 // 3][0].changeTerrain("ground", False)
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][0].changeTerrain("ground", False)
                    randomBiome[tilesPerSide // 2][0].changeTerrain("ground", False)
                    randomBiome[tilesPerSide * 3 // 4][0].changeTerrain("ground", False)
    
    # carve the paths using the recursive backtracking algorithm
    carveMaze(randomBiome)
    
    return randomBiome

def generateRandomMap(biomesPerMap, tilesPerSide):
    # creates a pseudo-random map and all the treasures on it

    # initialize the map and a list of biomes
    randomMap = []
    generatedBiomes = []

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
        generatedBiomes.append(generateRandomBiome(tilesPerSide, possibleExits, biomesPerMap, relevantPaths, i))
    
    for i in range(biomesPerMap):
        for j in range(len(generatedBiomes[i])):
            if i % int(math.sqrt(biomesPerMap)) == 0:
                randomMap.append(generatedBiomes[i][j])
            else:
                randomMap[i // int(math.sqrt(biomesPerMap)) * tilesPerSide + j] += generatedBiomes[i][j]
    
    return randomMap

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
        shov1 = pygame.image.load("tools/shovel 1.png")
        ax1 = pygame.image.load("tools/axe 1.png")
        pickax1 = pygame.image.load("tools/pickaxe 1.png")
        for tool in TOOLS:
            if tool == "shovel" and tool == currentTool:
                SCREEN.blit(shov, (50, 500))
            elif tool == "shovel" and tool != currentTool:
                SCREEN.blit(shov1, (50, 500))
            if tool == "axe" and tool == currentTool:
                SCREEN.blit(ax, (100, 500))
            if tool == "axe" and tool != currentTool:
                SCREEN.blit(ax1, (100, 500))
            if tool == "pickaxe" and tool == currentTool:
                SCREEN.blit(pickax, (150, 500))
            if tool == "pickaxe" and tool != currentTool:
                SCREEN.blit(pickax1, (150, 500))
        ##pygame.display.update()

        
    if inventoryTimer < 0.0:
        inventoryTimer = 0
    ##pygame.display.update()
    
    ##CLOCK.tick(FPS)

def useTool(row, col):
    if currentTool == "shovel":
        if grid[row][col].name == "ground":
            grid[row][col].changeTerrain("ground used", False)
            grid[row][col].isDestroyed = True
    elif currentTool == "axe":
        if grid[row][col].name == "tree":
            grid[row][col].changeTerrain("tree used", False)
            grid[row][col].isDestroyed = True
    elif currentTool == "pickaxe":
        if grid[row][col].name == "rock":
            grid[row][col].changeTerrain("rock used", False)
            grid[row][col].isDestroyed = True

def handleMenuEvents():
    # handle the events for the main menu
    pass

def handleGameEvents():
    global condition, currentTool, toolImage, toolTimer, printDebug
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
                inventoryTimer = 0.5
            elif event.key == cycleToolRightKey:
                if TOOLS.index(currentTool) == len(TOOLS) - 1:
                    currentTool = TOOLS[0]
                else:
                    currentTool = TOOLS[TOOLS.index(currentTool) + 1]
                toolImage = pygame.image.load("images/tools/" + currentTool + ".png")
                toolTimer = 0.5
                inventoryTimer = 0.5
            elif event.key == K_ESCAPE:
                condition = False
            elif event.key == K_x:
                printDebug = True
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
            elif event.key == useToolKey:
                pass
            elif event.key == cycleToolLeftKey:
                pass
            elif event.key == cycleToolRightKey:
                pass
            elif event.key == K_x:
                printDebug = False

def characterSelection():
    global biomesPerMap, biomeLength, condition, currentTool, grid, you
    currentName = 0
    while True:
        while condition:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    os._exit(0)
                elif event.type == KEYDOWN:
                    if event.key == moveLeftKey:
                        if currentName == 0:
                            currentName = 3
                        else:
                            currentName -= 1
                    elif event.key == moveRightKey:
                        if currentName == 3:
                            currentName = 0
                        else:
                            currentName += 1
                    elif event.key == useToolKey:
                        condition = False
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        os._exit(0)
            printTextToScreen(NAMES[currentName])

        condition = True
        grid = generateRandomMap(biomesPerMap, biomeLength)
        you = Player(biomeLength // 2, biomeLength // 2, 250, NAMES[currentName].lower())
        currentTool = getToolFromPlayerName(NAMES[currentName])
        you.checkForCollisions()

        while condition:
            executeGameFrame()
            
        condition = True


def printTextToScreen(textString):
    SCREEN.blit(title, (0, 0))
    fontObj = font.render(textString, True, YELLOW, BLACK)
    fontObj.set_colorkey(BLACK)
    SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
    pygame.display.update()
    CLOCK.tick(FPS)

def executeGameFrame():
    global timeLimit, toolTimer, inventoryTimer
    handleGameEvents()
    if "left" in you.direction and "right" in you.direction:
        you.direction.remove("left")
        you.direction.remove("right")
    if "down" in you.direction and "up" in you.direction:
        you.direction.remove("down")
        you.direction.remove("up")
    you.move()
    # render new frame: fill screen with solid color, blit the grid, and then blit the player
    SCREEN.fill((181, 230, 29))
    for i in range(len(screenGrid)):
        for j in range(len(screenGrid[0])):
            SCREEN.blit(screenGrid[i][j].image, (50 * (j - 1) - you.dispX, 50 * (i - 1) - you.dispY))
            if screenGrid[i][j].isDestroyed and screenGrid[i][j].treasure != 0:
                SCREEN.blit(screenGrid[i][j].treasure.image, (50 * (j - 1) - you.dispX, 50 * (i - 1) - you.dispY))
    SCREEN.blit(you.image, (you.x, you.y))
    if toolTimer > 0.0:
        SCREEN.blit(toolImage, (you.x + 5, you.y - 45))
    toolTimer -= timePassed
    if toolTimer < 0.0:
        toolTimer = 0.0
    if inventoryTimer > 0.0:
        showInventory()
    if inventoryTimer < 0.0:
        inventoryTimer = 0.0
    pygame.display.update()
    CLOCK.tick(FPS)

title = pygame.image.load("images/Title Card.png")
font = pygame.font.SysFont("helvetica", 32)

gameSelection = True
selection = 0
while True:
    while gameSelection:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                os._exit(0)
            elif event.type == KEYDOWN:
                if (event.key == moveLeftKey) or (event.key == moveRightKey):
                    if selection == 0:
                        selection = 1
                    elif selection == 1:
                        selection = 0
                elif event.key == useToolKey:
                    gameSelection = False
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    os._exit(0)
        printTextToScreen(MENU_OPTIONS[selection])

    if selection == 0:
        characterSelection()

    elif selection == 1:
        selection = 0
        while True:
            while condition:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        os._exit(0)
                    elif event.type == KEYDOWN:
                        if (event.key == moveLeftKey) or (event.key == moveRightKey):
                            if selection == 0:
                                selection = 1
                            elif selection == 1:
                                selection = 0
                        elif event.key == useToolKey:
                            condition = False
                        elif event.key == K_ESCAPE:
                            pygame.quit()
                            os._exit(0)
                SCREEN.blit(title, (0, 0))
                fontObj = font.render("Host a game or join a game?", True, YELLOW, BLACK)
                fontObj.set_colorkey(BLACK)
                SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
                fontObj2 = font.render(OPTIONS[selection], True, YELLOW, BLACK)
                fontObj2.set_colorkey(BLACK)
                SCREEN.blit(fontObj2, (SCREEN_WIDTH // 2 - fontObj2.get_width() // 2, 450))
                pygame.display.update()
                CLOCK.tick(FPS)

            if selection == 0:
                #Start server
                IPAddr = nf.fGetIP()
                printTextToScreen("Your IP is: " + IPAddr)
                serverSocket = nf.fCreateServer(PORT)

                flag = True
                while flag:
                    try:
                        serverSocket.settimeout(5) #Time server waits for client to connect
                        serverConnection = nf.fCreateConnection(serverSocket)
                    except socket.timeout:
                        printTextToScreen("Client failed to connect.")
                        time.sleep(5)
                        nf.fCloseServer(serverSocket)
                        pygame.quit()
                        os._exit(0)
                        break
                    except:
                        raise
                    else:
                        printTextToScreen("Client connected.")

                        nf.fSendToClient(serverConnection, "connected")

                        time.sleep(5)
                        nf.fCloseServer(serverSocket) #this is for debugging
                        pygame.quit()
                        os._exit(0)
                        
                        #send/receive here
                        flag = False
            elif selection == 1:
                #Start client
                printTextToScreen("What is the host's IP?")
                pygame.draw.rect(SCREEN, (0,0,0), (100,450,345,35))
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
                    pygame.draw.rect(SCREEN, (0,0,0), (100,450,350,35)) 
                    SCREEN.blit(fontObj2, (SCREEN_WIDTH // 2 - fontObj2.get_width() // 2, 450))
                    pygame.display.update()
                    CLOCK.tick(FPS)

                clientSocket = nf.fCreateClient(ipStr, PORT)
                printTextToScreen("Connecting...")
                data = nf.fReceiveFromServer(clientSocket)
                if data == "connected":
                    printTextToScreen("Successfully connected.")
                #else:
                    
                nf.fCloseClient(clientSocket)  #this is for debugging
                time.sleep(5)
                pygame.quit()
                os._exit(0)
        



    


        
        
        
