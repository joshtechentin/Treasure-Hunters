# All classes/functions NOT relating to the server/client or pygame go here!
# Classes should be declared BEFORE the functions

import math, random
from mainProgram import Terrain

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
                biome[i][j] = Terrain("ground", 0)
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
            biome[edge[2]][edge[3]] = Terrain("ground", 0)
            junctionSets.remove(set1)
            junctionSets.remove(set2)
            newJunction = set1.union(set2)
            junctionSets.append(newJunction)

    return biome

def generateRandomBiome(tilesPerSide, possibleExits, BPS, paths):
    # generates a random biome that is a part of the world map (e.g. forest)
    biomeName = random.choice(biomes)
    
    # initialize the biome as a 2D list of all 0s
    randomBiome = [[Terrain(getTerrainFromBiome(biomeName), 0)] * tilesPerSide for i in range(tilesPerSide)]

    # change all chosen exits to a moveable path
    for path in sorted(paths):
        if paths[path][1]:
            if paths[path][0] == "down":
                if possibleExits == 1:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2] = Terrain("ground", 0)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide - 1][tilesPerSide // 3] = Terrain("ground", 0)
                    randomBiome[tilesPerSide - 1][tilesPerSide * 2 // 3] = Terrain("ground", 0)
                else: # defaults to 3
                    randomBiome[tilesPerSide - 1][tilesPerSide // 4] = Terrain("ground", 0)
                    randomBiome[tilesPerSide - 1][tilesPerSide // 2] = Terrain("ground", 0)
                    randomBiome[tilesPerSide - 1][tilesPerSide * 3 // 4] = Terrain("ground", 0)
            elif paths[path][0] == "up":
                if possibleExits == 1:
                    randomBiome[0][tilesPerSide // 2] = Terrain("ground", 0)
                elif possibleExits == 2:
                    randomBiome[0][tilesPerSide // 3] = Terrain("ground", 0)
                    randomBiome[0][tilesPerSide * 2 // 3] = Terrain("ground", 0)
                else: # defaults to 3
                    randomBiome[0][tilesPerSide // 4] = Terrain("ground", 0)
                    randomBiome[0][tilesPerSide // 2] = Terrain("ground", 0)
                    randomBiome[0][tilesPerSide * 3 // 4] = Terrain("ground", 0)
            elif paths[path][0] == "right":
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1] = Terrain("ground", 0)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][tilesPerSide // 3] = Terrain("ground", 0)
                    randomBiome[tilesPerSide * 2 // 3][tilesPerSide - 1] = Terrain("ground", 0)
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][tilesPerSide - 1] = Terrain("ground", 0)
                    randomBiome[tilesPerSide // 2][tilesPerSide - 1] = Terrain("ground", 0)
                    randomBiome[tilesPerSide * 3 // 4][tilesPerSide - 1] = Terrain("ground", 0)
            else: # defaults to left
                if possibleExits == 1:
                    randomBiome[tilesPerSide // 2][0] = Terrain("ground", 0)
                elif possibleExits == 2:
                    randomBiome[tilesPerSide // 3][0] = Terrain("ground", 0)
                    randomBiome[tilesPerSide * 2 // 3][0] = Terrain("ground", 0)
                else: # defaults to 3
                    randomBiome[tilesPerSide // 4][0] = Terrain("ground", 0)
                    randomBiome[tilesPerSide // 2][0] = Terrain("ground", 0)
                    randomBiome[tilesPerSide * 3 // 4][0] = Terrain("ground", 0)
    
    # carve the paths using the recursive backtracking algorithm
    carveMaze(randomBiome)
    
    return randomBiome

def generateRandomMap(biomesPerMap, tilesPerSide):
    # creates a pseudo-random map and all the treasures on it

    # initialize the map as a list of biomes
    randomMap = []

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
        randomMap.append(generateRandomBiome(tilesPerSide, possibleExits, biomesPerMap, relevantPaths))

    return randomMap
