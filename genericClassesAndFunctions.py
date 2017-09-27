# All classes/functions NOT relating to the server/client or pygame go here!
# Classes should be declared BEFORE the functions

import random

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

def generateRandomScreen(biome, tilesPerScreen):
    # generates a random screen in a biome
    # uses a random maze generation algorithm, making sure there is an exit in each direction    

    # initialize the screen as a list of tiles
    screen = []

    # more stuff to go here

    return screen

def generateRandomBiome(screensPerBiome, tilesPerScreen):
    # generates a random biome that is a part of the world map (e.g. forest)

    # select a random biome to make
    biome = random.choice(biomes)
    
    # initialize the biome as a list of screens
    randomBiome = []
    
    # fill the biome with randomly generated screens
    for i in range(screenPerBiome):
        randomBiome.append(generateRandomScreen(biome, tilesPerScreen))
    return randomBiome

def generateRandomMap(biomesPerMap, screensPerBiome, tilesPerScreen):
    # creates a pseudo-random map and all the treasures on it

    # initialize the map as a list of biomes
    randomMap = []

    # fill the map with randomly generated biomes
    for i in range(biomesPerMap):
        randomMap.append(generateRandomBiome(screensPerBiome, tilesPerScreen))
    return randomMap
