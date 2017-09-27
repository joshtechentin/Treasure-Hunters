# Design standards:
#
# Constants are in ALL_CAPS with underscores to separate words
# Other variables/functions are in camelCase starting with a lowercase letter
# Classes are in CamelCase starting with a captial letter
# Local variables declared within a function MUST begin with 'lcl'
# Give any construct a descriptive name to avoid duplicate names

import pygame, os, pickle, math
from pygame.locals import *
from genericClassesAndFunctions import *
from networkFunctions import *

pygame.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Treasure Hunters")

CLOCK = pygame.time.Clock()
FPS = 30

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
horizontalRooms = 5
verticalRooms = 5

class Treasure(object):
    def __init__(self, name):
        self.x = None # the x-coordinate of the treasure; it is null until exposed
        self.y = None # the y-coordinate of the treasure; it is null until exposed
        self.name = name # the type of treasure it is
        self.value = genericClassesAndFunctions.getTreasureValueFromName(name) # the amount of money the treasure is worth
        self.image = pygame.image.load("images/treasure/" + name + ".png")

class Terrain(object):
    def __init__(self, roomX, roomY, row, col, name, treasure):
        self.room = (roomX, roomY) # coordinates of the terrain's room
        self.row = row # the row the terrain is located at in the room
        self.col = col # the column the terrain is located at in the room
        self.name = name # the type of terrain it is (e.g. tree, rock, etc)
        self.image = pygame.image.load("images/terrain/" + name + ".png")
        self.gem = gem # the gem included inside the terrain, if any

class Player(object):
    def __init__(self, x, y, speed, name):
        self.x = x # the x-coordinate of the player
        self.y = y # the y-coordinate of the player
        self.speed = speed # the speed of the player (in pixels per second)
        self.movement = self.speed / FPS # the amount of pixels they move each frame
        self.diagonalMovement = self.movement * math.cos(45) # the amount of pixels they move each frame diagonally
        self.name = name # the player's name, used to determine many things
        self.image = pygame.image.load("images/characters/" + name + ".png")
        self.money = 0 # the money the player has gained
        self.currentTool = genericClassesAndFunctions.getToolFromPlayerName(name) # the tool equipped by the player; initialized to their starting tool
        self.tools = [self.currentTool]
        self.animationFrame = 0 # keeps track of which image to render in an animation
    def animate(self):
        if self.animationFrame < 1:
            self.animationFrame += 1
        else:
            self.animationFrame = 0
    def checkForCollisions(self):
        
    def move(self, direction):
        # moves player in the direction specified and animates them
        # if the direction is a compass direction, they move far
        # if the direction is a diagonal, they move less (picture unit circle)
        if direction == "right":
            self.x += self.movement
        elif direction == "left":
            self.x -= self.movement
        elif direction == "down":
            self.y += self.movement
        elif direction == "up":
            self.y -= self.movement
        elif direction == "down-right":
            self.x += self.diagonalMovement
            self.y += self.diagonalMovement
        elif direction == "up-right":
            self.x += self.diagonalMovement
            self.y -= self.diagonalMovement
        elif direction == "down-left":
            self.x -= self.diagonalMovement
            self.y += self.diagonalMovement
        elif direction == "up-left":
            self.x -= self.diagonalMovement
            self.y -= self.diagonalMovement
        self.checkForCollisions()


def handleMenuEvents():
    for event in pygame.event.get():
        

def handleGameEvents():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            os._exit(1)
        if event.type == KEYDOWN:
            if event.key == moveLeftKey:

            elif event.key == moveRightKey:

            elif event.key == moveDownKey:

            elif event.key == moveUpKey:

            elif event.key == useToolKey:

            elif event.key == cycleToolLeftKey:

            elif event.key == cycleToolRightKey:

        if event.type == KEYUP:
            if event.key == moveLeftKey:

            elif event.key == moveRightKey:

            elif event.key == moveDownKey:

            elif event.key == moveUpKey:

            elif event.key == useToolKey:

            elif event.key == cycleToolLeftKey:

            elif event.key == cycleToolRightKey:


def executeGameFrame():
    handleGameEvents()
    pygame.display.update()
    CLOCK.tick(FPS)
