#!/usr/bin/env python3

from copy import copy, deepcopy
from operator import ne
from os import curdir
from random import randrange


# A cell in the panel, with Color 0 and in Region 0 by default
class Cell:
    
    def __init__(self, color=0):
        self.color = color
        self.region = 0


# Print a panel of cells or verts
# x is left-to-right, y is bottom-to-top
def printPanel(panel, displayAttribute=""):
    for y in reversed(range(len(panel[0]))):
        for x in range(len(panel)):
                if (len(displayAttribute) > 0):
                    value = getattr(panel[x][y], displayAttribute)
                else:
                    value = panel[x][y]
                print(value, end=(" " * (max(0, (3 + (-1 * len(str(panel[x][y]))))))))
        print()


# Determine xMax and yMax based on structure
def calcCoordMaxPosition(structure):
    return (len(structure)-1, len(structure[0])-1)


# Generate and return an arrangement of properly-visited verts
def genVertPath(passVerts, currentPosition, vertValue):

    # Deepcopy verts in order to avoid reference shenanigans
    verts = deepcopy(passVerts)
    verts[currentPosition[0]][currentPosition[1]] = vertValue
    
    # Maximum vert coords
    maxPosition = calcCoordMaxPosition(verts)

    # Return if path finished
    if (currentPosition == maxPosition):
        return verts
    
    # Find connected vert coords, and if none exist return False
    connectedVertCoords = findConnectedVertCoords(maxPosition, currentPosition)
    if (not connectedVertCoords):
        return False

    # Recursion time - choose a random connected vert and check it out
    while (connectedVertCoords):
        nextVertCoords = connectedVertCoords.pop(randrange(len(connectedVertCoords)))
        if (verts[nextVertCoords[0]][nextVertCoords[1]] == 0):
            path = genVertPath(verts, nextVertCoords, vertValue + 1)
            if (path):
                return path
    return False


# Find the coords of all verts connected to a specific vert, and return the coords as a list of tuples
def findConnectedVertCoords(maxPosition, currentPosition):

    connectedVertCoords = []

    # Make sure verts this function provides won't be off-panel
    # Recursion speedup - don't bother checking coords unless the path can escape
    if (currentPosition[0] != maxPosition[0]):
        connectedVertCoords.append((currentPosition[0]+1,currentPosition[1]))
    if (currentPosition[1] != maxPosition[1]):
        connectedVertCoords.append((currentPosition[0],currentPosition[1]+1))
    if ((currentPosition[0] != maxPosition[0]) and (currentPosition[1] != 0)):
        connectedVertCoords.append((currentPosition[0],currentPosition[1]-1))
    if ((currentPosition[1] != maxPosition[1]) and (currentPosition[0] != 0)):
        connectedVertCoords.append((currentPosition[0]-1,currentPosition[1]))
    
    return connectedVertCoords


# Generate and return an x-by-y list-of-lists
def genEmptyStructure(dimensions, value):
    x, y = dimensions
    columns = []
    for _ in range(x):
        row = []
        for _ in range(y):
            row.append(copy(value))
        columns.append(row)
    return columns


# Find and return the two vert coords surrounding a transform from cell position
def getVertCoordsSurroundingCrawl(currentPosition, transform):

    coords = []

    # Top-right and bottom-left corners
    if (transform[0] == 1 or transform[1] == 1):
        coords.append(tuple(map(sum, zip(currentPosition, (1, 1)))))
    else:
        coords.append(currentPosition)

    # Top-left and bottom-right corners
    if (transform[0] - transform[1] == -1):
        coords.append((currentPosition[0], currentPosition[1] + 1))
    else:
        coords.append((currentPosition[0] + 1, currentPosition[1]))

    return coords


# Check if moving from current position to the next is blocked, and if not, return the next position
def checkIfCrawlNotBlocked(currentPosition, cells, verts, maxPosition, transform):

    # Determine next position
    nextPosition = tuple(map(sum, zip(currentPosition, transform)))

    # Check if next position greater than max position
    for i in range(len(nextPosition)):
        if (nextPosition[i] < 0 or nextPosition[i] > maxPosition[i]):
            return False
    
    # Check if next cell's region has been set
    if (cells[nextPosition[0]][nextPosition[1]].region != 0):
        return False

    # Check if vert path blocks crawl
    coords = getVertCoordsSurroundingCrawl(currentPosition, transform)
    vertValues = [verts[coords[0][0]][coords[0][1]], verts[coords[1][0]][coords[1][1]]]
    if (abs(vertValues[0] - vertValues[1]) == 1 and 
        vertValues[0] != 0 and
        vertValues[1] != 0):
        return False
    
    return nextPosition


# Recursively crawl between cells in a region, assigning the appropriate region index
def crawlThroughCells(currentPosition, cells, verts, maxPosition, regionIndex):

    # Set appropriate region index
    cells[currentPosition[0]][currentPosition[1]].region = regionIndex

    # For each direction, if crawl valid, recurse with adjacent cell
    transforms = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for transform in transforms:
        nextPosition = checkIfCrawlNotBlocked(currentPosition, cells, verts, maxPosition, transform)
        if (nextPosition):
            cells = crawlThroughCells(nextPosition, cells, verts, maxPosition, regionIndex)

    # Once transforms exhausted, return updated cells structure
    return cells


# Determine regions based off of vert path, returning adjusted cells
def findCellRegions(passCells, verts):

    # Deepcopy cells in order to avoid reference shenanigans
    cells = deepcopy(passCells)

    # Determine regions for all cells
    regionIndex = 1
    for x in range(len(cells)):
        for y in range(len(cells[0])):
            if (cells[x][y].region == 0):
                # Crawl and assign regions
                cells = crawlThroughCells((x, y), cells, verts, calcCoordMaxPosition(cells), regionIndex)
                regionIndex += 1

    return cells


# Use region values to assign colors to each cell
def assignCellColors(cells, colors, minSquaresPerRegion, maxSquaresPerRegion):

    # Add all cells to region dictionary
    regions = {}
    regionIndex = 1
    nextRegionFound = True
    while (nextRegionFound):
        nextRegionFound = False
        for column in cells:
            for cell in column:
                if (cell.region == regionIndex):
                    nextRegionFound = True
                    if regionIndex not in regions.keys():
                        regions[regionIndex] = [cell]
                    else:
                        regions[regionIndex].append(cell)
        regionIndex += 1

    # Assign random number of squares to each region
    nextColorIndex = len(colors)
    for i in range(regionIndex-1)[1:]:
        if (maxSquaresPerRegion < 0):
            value = max(min(minSquaresPerRegion, len(regions[i])), randrange(max(1, (len(regions[i]) - 1))))
        else:
            value = min(maxSquaresPerRegion, max(min(minSquaresPerRegion, len(regions[i])), randrange(max(1, (len(regions[i]) - 1)))))
        if (value > 0):
            for _ in range(0, value):
                regions[i].pop(randrange(len(regions[i]))).color = (nextColorIndex % len(colors)) + 1
        nextColorIndex += 1

    return cells


# From cells structure, generate and return a looksy-foreground-gen placement string argument
def genPlacementString(cells):
    output = ""
    firstInColumn = True
    for y in reversed(range(len(cells[0]))):
        if (not firstInColumn):
                output += "-"
        firstInColumn = False
        firstInRow = True
        for x in range(len(cells)):
            if (not firstInRow):
                output += ","
            firstInRow = False
            output += str(min(1, cells[x][y].color))
            output += f"c{str(cells[x][y].color)}"
    return output


# Using panel dimensions tuple and a colors list, generate and return a looksy-foreground-gen args string
def genForegroundArgs(dimensions, colors, min, max):

    # Define verts structure
    verts = genEmptyStructure((dimensions[0] + 1, dimensions[1] + 1), 0)

    # Generate vert path to base regions off of
    verts = genVertPath(verts, (0, 0), 1)

    # Define cells structure
    cells = genEmptyStructure((dimensions[0], dimensions[1]), Cell())

    # Use vert path to determine regions
    cells = findCellRegions(cells, verts)

    # Use region values to assign colors to each cell
    cells = assignCellColors(cells, colors, min, max)
    # printPanel(cells, "color")
    placements = genPlacementString(cells)

    return f"square {','.join(colors)} {dimensions[0]},{dimensions[1]} {placements}"
