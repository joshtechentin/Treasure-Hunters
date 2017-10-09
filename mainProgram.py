# Design standards:
#
# Constants are in ALL_CAPS with underscores to separate words
# Other variables/functions are in camelCase starting with a lowercase letter
# Classes are in CamelCase starting with a captial letter
# Give any construct a descriptive name to avoid duplicate names

import pygame, os, pickle, math, random
from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 550
SCREEN_HEIGHT = 550
SCREEN_GRID_WIDTH = 11
SCREEN_GRID_HEIGHT = 11
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FULLSCREEN, 32)
pygame.display.set_caption("Treasure Hunters")

CLOCK = pygame.time.Clock()
FPS = 30

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
biomesPerMap = 9 # MUST be equal a whole number squared
biomeSize = 11 # MUST be equal to 3+4n where n is a whole number >= 0

# main game variables
grid = [[]]
you = 0

biomes = ["forest", "quarry", "desert", "arctic", "plains"]

def getTreasureValueFromName(name):
    # returns the value of a treasure based on its name
    # these values have NOT been finalized
    
    if name == "diamond":
        return 1000
    elif name == "ruby":
        return 100
    elif name == "gold coin":
        return 10
    else:
        return 1

def getToolFromPlayerName(name):
    # returns the default tool the given player starts with
    # the names and values have NOT been finalized

    if name == "Josh":
        return "shovel"
    elif name == "Anthony":
        return "axe"
    elif name == "Caitlin":
        return "pickax"
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
        return "ice"
    elif biome == "plains":
        return "tree"

class Treasure(object):
    def __init__(self, name):
        self.x = None # the x-coordinate of the treasure; it is null until exposed
        self.y = None # the y-coordinate of the treasure; it is null until exposed
        self.name = name # the type of treasure it is
        self.value = getTreasureValueFromName(name) # the amount of money the treasure is worth
        self.image = pygame.image.load("images/treasure/" + name + ".png")

class Terrain(object):
    def __init__(self, row, col, name, treasure):
        self.row = row
        self.col = col
        self.name = name # the type of terrain it is (e.g. tree, rock, etc)
        self.image = pygame.image.load("images/terrain/" + name + ".png")
        self.treasure = treasure # the gem included inside the terrain, if any
    
    def changeTerrain(self, name):
        # changes terrain to a new terrain
        self.name = name
        self.image = pygame.image.load("images/terrain/" + name + ".png")
    
    def checkIfSolid(self):
        # returns if the terrain is solid or not
        if self.name != "ground":
            return True
        return False
            
class Player(object):
    def __init__(self, row, col, speed, name):
        self.x = 250
        self.y = 250
        self.dispX = 0 # the amount of horizontal displacement the player experiences relative to the grid square
        self.dispY = 0 # the amount of vertical displacement the player experiences relative to the grid square
        self.row = row # the row the player is on on the grid
        self.col = col # the column the players is on on the grid
        self.speed = speed # the speed of the player (in pixels per second)
        self.movement = self.speed / FPS # the amount of pixels they move each frame
        self.diagonalMovement = self.movement * math.cos(45) # the amount of pixels they move each frame diagonally
        self.direction = [] # keeps track of which direction(s) the player is moving in
        self.collisionGrid = [[grid[row][col], grid[row][col + 1]], [grid[row + 1][col], grid[row + 1][col + 1]]]
        self.name = name # the player"s name, used to determine many things
        self.orientation = "front"
        self.animationFrame = 1 # keeps track of which image to render in an animation
        self.image = pygame.image.load("images/characters/" + name + "/" + self.orientation + " " + str(self.animationFrame) + ".png")
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
        #for i in self.collisionGrid:
        #    for j in i:
        #        if j.checkIfSolid():
        #            if self.row * 50 + self.dispX > (j.row * 50) and self.row * 50 < (j.row * 50) + j.image.get_width(): # check if x's overlap
        #                if self.col * 50 + self.dispY > (j.col * 50) and self.col * 50 < (j.col * 50) + j.image.get_height(): # check if y's overlap
        #                    if "right" in self.direction and "down" in self.direction:
        #                        if self.row * 50 + self.dispX - (j.row * 50) < self.col * 50 + self.dispY - (j.col * 50):
         #                           self.dispX -= self.row * 50 + self.dispX - (j.row * 50)
          #                      else:
           #                         self.dispY -= self.col * 50 + self.dispY - (j.col * 50)
            #                elif "right" in self.direction and "up" in self.direction:
             #                   if self.x + self.image.get_width() - (j.col * 50) < (j.col * 50) + j.image.get_height() - self.y:
              #                      self.dispX = (j.row * 50) - self.image.get_width()
               #                 else:
                #                    self.dispY = (j.col * 50) + j.image.get_height()
                 #           elif "right" in self.direction:
                  #              self.x = (j.row * 50) - self.image.get_width()
                   #         elif "left" in self.direction and "down" in self.direction:
                    #            if (j.row * 50) + j.image.get_width() - self.x < self.y + self.image.get_height() - (j.col * 50):
                     #               self.dispX = (j.row * 50) + j.image.get_width()
                      #          else:
                       #             self.dispY = (j.col * 50) - self.image.get_height()
                        #    elif "left" in self.direction and "up" in self.direction:
                         #       if (j.row * 50) + j.image.get_width() - self.x < (j.col * 50) + j.image.get_height() - self.y:
                          #          self.dispX = (j.row * 50) + j.image.get_width()
                           #     else:
                            #        self.dispY = (j.col * 50) + j.image.get_height()
                            #elif "left" in self.direction:
                            #    self.dispX = (j.row * 50) + j.image.get_width()
                            #elif "down" in self.direction:
                            #    self.dispY = (j.col * 50) - self.image.get_height()
                            #elif "up" in self.direction:
                            #   self.dispY = (j.col * 50) + j.image.get_height()
        if self.dispX >= 50:
            self.row += 1
            if self.row >= len(grid):
                self.row = 0
            self.dispX -= 50
        elif self.dispX <= -50:
            self.row -= 1
            if self.row < 0:
                self.row = len(grid) - 1
            self.dispX += 50
        if self.dispY >= 50:
            self.col += 1
            if self.col >= len(grid[0]):
                self.col = 0
            self.dispY -= 50
        elif self.dispY <= -50:
            self.col -= 1
            if self.col < 0:
                self.col = len(grid[0]) - 1
            self.dispY += 50
        self.updateCollisionGrid()
        updateScreenGrid()
                        
    def updateCollisionGrid(self):
        # call when the user has finished moving for the current frame.
        # updates the collision grid with the user"s grid position
        # and the grid square to their right, down, and down-right
        self.collisionGrid[0][0] = grid[self.row][self.col]
        # account for world map wrapping
        if self.row == len(grid) - 1: # check if player is in the rightmost column
            self.collisionGrid[1][0] = grid[0][self.col]
            if self.col == len(grid[0]) - 1: # check if the player is at the downmost row
                self.collisionGrid[0][1] = grid[self.row][0]
                self.collisionGrid[1][1] = grid[0][0]
            else:
                self.collisionGrid[0][1] = grid[self.row][self.col + 1]
                self.collisionGrid[1][1] = grid[0][self.col + 1]
        else:
            self.collisionGrid[1][0] = grid[self.row + 1][self.col]
            if self.col == len(grid[0]) - 1: # check if the player is at the downmost row
                self.collisionGrid[0][1] = grid[self.row][0]
                self.collisionGrid[1][1] = grid[self.row + 1][0]
            else:
                self.collisionGrid[0][1] = grid[self.row][self.col + 1]
                self.collisionGrid[1][1] = grid[self.row + 1][self.col + 1]
                
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
            self.checkForCollisions()
        else:
            self.animationFrame = 1
        self.changeImage()

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
                biome[i][j].changeTerrain("ground")
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
            biome[edge[2]][edge[3]].changeTerrain("ground")
            junctionSets.remove(set1)
            junctionSets.remove(set2)
            newJunction = set1.union(set2)
            junctionSets.append(newJunction)

    return biome

def generateRandomBiome(tilesPerSide, possibleExits, BPM, paths, num):
    # generates a random biome that is a part of the world map (e.g. forest)
    biomeName = random.choice(biomes)
    
    # initialize the biome as a 2D list of all 0s
    randomBiome = [[0] * tilesPerSide for i in range(tilesPerSide)]
    for i in range(tilesPerSide):
        for j in range(tilesPerSide):
            randomBiome[i][j] = Terrain(num // int(math.sqrt(BPM)) * tilesPerSide + i, num % int(math.sqrt(BPM)) * tilesPerSide + j, getTerrainFromBiome(biomeName), 0)

    # change all chosen exits to a moveable path
    for path in sorted(paths):
        if paths[path][1]:
            if paths[path][0] == "down":
                if possibleExits == 1:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2].changeTerrain("ground")
                elif possibleExits == 2:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 3].changeTerrain("ground")
                    randomBiome[tilesPerSide - 1][tilesPerSide * 2 // 3].changeTerrain("ground")
                else: # defaults to 3
                    randomBiome[tilesPerSide - 1][tilesPerSide // 4].changeTerrain("ground")
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2].changeTerrain("ground")
                    randomBiome[tilesPerSide - 1][tilesPerSide * 3 // 4].changeTerrain("ground")
            elif paths[path][0] == "up":
                if possibleExits == 1:
                    randomBiome[0][tilesPerSide // 2].changeTerrain("ground")
                elif possibleExits == 2:
                    randomBiome[0][tilesPerSide // 3].changeTerrain("ground")
                    randomBiome[0][tilesPerSide * 2 // 3].changeTerrain("ground")
                else: # defaults to 3
                    randomBiome[0][tilesPerSide // 4].changeTerrain("ground")
                    randomBiome[0][tilesPerSide // 2].changeTerrain("ground")
                    randomBiome[0][tilesPerSide * 3 // 4].changeTerrain("ground")
            elif paths[path][0] == "right":
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1].changeTerrain("ground")
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][tilesPerSide // 3].changeTerrain("ground")
                    randomBiome[tilesPerSide * 2 // 3][tilesPerSide - 1].changeTerrain("ground")
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][tilesPerSide - 1].changeTerrain("ground")
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1].changeTerrain("ground")
                    randomBiome[tilesPerSide * 3 // 4][tilesPerSide - 1].changeTerrain("ground")
            else: # defaults to left
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][0].changeTerrain("ground")
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][0].changeTerrain("ground")
                    randomBiome[tilesPerSide * 2 // 3][0].changeTerrain("ground")
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][0].changeTerrain("ground")
                    randomBiome[tilesPerSide // 2][0].changeTerrain("ground")
                    randomBiome[tilesPerSide * 3 // 4][0].changeTerrain("ground")
    
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

grid = generateRandomMap(biomesPerMap, biomeSize) # the main grid containing every piece of terrain and its location
screenGrid = [[0] * 13 for i in range(13)]
you = Player(5, 5, 250, "Josh")

def updateScreenGrid():
    global screenGrid
    for i in range(13):
        for j in range(13):
            gridX = you.row - 6 + i
            if gridX >= biomeSize * int(math.sqrt(biomesPerMap)):
                gridX -= biomeSize * int(math.sqrt(biomesPerMap))
            elif gridX <= -biomeSize * int(math.sqrt(biomesPerMap)):
                gridX += biomeSize * int(math.sqrt(biomesPerMap))
            gridY = you.col - 6 + j
            if gridY >= biomeSize * int(math.sqrt(biomesPerMap)):
                gridY -= biomeSize * int(math.sqrt(biomesPerMap))
            elif gridY <= -biomeSize * int(math.sqrt(biomesPerMap)):
                gridY += biomeSize * int(math.sqrt(biomesPerMap))
            screenGrid[i][j] = grid[gridX][gridY]

updateScreenGrid()

def handleMenuEvents():
    # handle the events for the main menu
    pass

def handleGameEvents():
    global condition
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
                pass
            elif event.key == cycleToolLeftKey:
                pass
            elif event.key == cycleToolRightKey:
                pass
            elif event.key == K_ESCAPE:
                condition = False
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

def executeGameFrame():
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
            SCREEN.blit(screenGrid[i][j].image, (50 * (i - 1) - you.dispX, 50 * (j - 1) - you.dispY))
    SCREEN.blit(you.image, (you.x, you.y))
    pygame.display.update()
    CLOCK.tick(FPS)

title = pygame.image.load("images/Title Card.png")
names = ["Anthony", "Caitlin", "Josh", "Matt"]
currentName = 0
font = pygame.font.SysFont("helvetica", 32)

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
        SCREEN.blit(title, (0, 0))
        fontObj = font.render(names[currentName], True, (255, 255, 0), (0, 0, 0))
        fontObj.set_colorkey((0, 0, 0))
        SCREEN.blit(fontObj, (SCREEN_WIDTH // 2 - fontObj.get_width() // 2, 400))
        pygame.display.update()
        CLOCK.tick(FPS)

    condition = True
    grid = generateRandomMap(biomesPerMap, biomeSize)
    you = Player(5, 5, 250, names[currentName].lower())
    you.checkForCollisions()

    while condition:
        executeGameFrame()

    condition = True
