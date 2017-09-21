# Design standards:
#
# Constants are in ALL_CAPS with underscores to separate words
# Other variables/functions are in camelCase
# Functions MUST start with 'f'
# Classes are in CamelCase starting with a captial letter
# Local variables declared within a function MUST begin with 'lcl'

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
MOVE_LEFT_KEY = K_LEFT
MOVE_RIGHT_KEY = K_RIGHT
MOVE_DOWN_KEY = K_DOWN
MOVE_UP_KEY = K_UP
USE_TOOL_KEY = K_z
CYCLE_TOOL_LEFT_KEY = K_a
CYCLE_TOOL_RIGHT_KEY = K_s

def fHandleGameEvents():
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

def fExecuteFrame():
    fHandleGameEvents()
    pygame.display.update()
    CLOCK.tick(FPS)
