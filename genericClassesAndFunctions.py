# All classes/functions NOT relating to the server/client or pygame go here!
# Classes should be declared BEFORE the functions

import random

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

def fGenerateRandomScreen():
    # generates a random screen in a biome

def fGenerateRandomBiome():
    # generates a random biome that is a part of the world map (e.g. forest)

def fGenerateRandomMap():
    # creates a pseudo-random map and all the treasures on it
