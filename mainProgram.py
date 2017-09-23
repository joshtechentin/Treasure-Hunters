# Design standards:
#
# Constants are in ALL_CAPS with underscores to separate words
# Other variables/functions are in camelCase
# Classes are in CamelCase starting with a captial letter
# Local variables declared within a function MUST begin with 'lcl'
# Give any construct a descriptive name to avoid duplicate names

import pygame, os, pickle
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
MOVE_LEFT_KEY = K_LEFT
MOVE_RIGHT_KEY = K_RIGHT
MOVE_DOWN_KEY = K_DOWN
MOVE_UP_KEY = K_UP
USE_TOOL_KEY = K_z
CYCLE_TOOL_LEFT_KEY = K_a
CYCLE_TOOL_RIGHT_KEY = K_s

# default game settings
# these can be changed in the options menu
TIME_LIMIT = 300.0 # time limit in seconds
HORIZONTAL_ROOMS = 5
VERTICAL_ROOMS = 5

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
    def __init__(self, x, y, name):
        self.x = x # the x-coordinate of the player
        self.y = y # the y-coordinate of the player
        self.name = name # the player's name, used to determine many things
        self.image = pygame.image.load("images/characters/" + name + ".png")
        self.money = 0 # the money the player has gained
        self.currentTool = genericClassesAndFunctions.getToolFromPlayerName(name) # the tool equipped by the player; initialized to their starting tool
        self.tools = [self.currentTool]


def handleGameEvents():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            os._exit(1)
        if event.type == KEYDOWN:
            if event.key == MOVE_LEFT_KEY:

            elif event.key == MOVE_RIGHT_KEY:

            elif event.key == MOVE_DOWN_KEY:

            elif event.key == MOVE_UP_KEY:

            elif event.key == USE_TOOL_KEY:

            elif event.key == CYCLE_TOOL_LEFT_KEY:

            elif event.key == CYCLE_TOOL_RIGHT_KEY:

        if event.type == KEYUP:
            if event.key == MOVE_LEFT_KEY:

            elif event.key == MOVE_RIGHT_KEY:

            elif event.key == MOVE_DOWN_KEY:

            elif event.key == MOVE_UP_KEY:

            elif event.key == USE_TOOL_KEY:

            elif event.key == CYCLE_TOOL_LEFT_KEY:

            elif event.key == CYCLE_TOOL_RIGHT_KEY:

def executeFrame():
    handleGameEvents()
    pygame.display.update()
    CLOCK.tick(FPS)
