import math
from collections import defaultdict
import numpy as np


def linesToVoxels(lineList, pixels):
    for x in range(len(pixels)):
        isBlack = False
        lines = list(filter(lambda line: isRelevantLines(line, x, pixels), lineList))
        targetYs = list(map(lambda line: int(generateY(line, x)),lines))
        for y in range(len(pixels[x])):
            if isBlack:
                pixels[x][y] = True
            if y in targetYs:
                for line in lines:
                    if onLine(line, x, y):
                        isBlack = not isBlack
                        pixels[x][y] = True

        if isBlack:
            print("an error has occured at x%sz%s" % (x, lineList[0][0][2]))


def isRelevantLines(line, x, pixels):
    above = list(filter(lambda pt: pt[0] > x, line))
    below = list(filter(lambda pt: pt[0] < x, line))
    same = list(filter(lambda pt: pt[0] == x, line))
    if above and below:
        return True
    elif same and above:
        return True
    elif len(same) == 2:
        start = min(int(same[0][1]), int(same[1][1]))
        stop = max(int(same[0][1]), int(same[1][1])) + 1
        for y in range(start, stop):
            pixels[x][y] = True
    else:
        return False


def generateY(line, x):
    if line[1][0] == line[0][0]:
        return -1
    ratio = (x - line[0][0]) / (line[1][0] - line[0][0])
    ydist = line[1][1] - line[0][1]
    newy = line[0][1] + ratio * ydist
    return newy


def onLine(line, x, y):
    newy = generateY(line, x)
    if int(newy) != y:
        return False
    if int(line[0][0]) != x and int(line[1][0]) != x and (max(line[0][0], line[1][0]) < x or min(line[0][0], line[1][0]) > x):
        return False
    if int(line[0][1]) != y and int(line[1][1]) != y and (max(line[0][1], line[1][1]) < y or min(line[0][1], line[1][1]) > y):
        return False
    return True
