import math
import poly_tri
from collections import defaultdict
import matplotlib.pyplot as plt


def fillPerimeter(lineList, pixels):
    for x in range(len(pixels)):
        isBlack = False
        lines = list(findRelevantLines(lineList, x))

        for y in range(len(pixels[x])):
            if isBlack:
                pixels[x][y] = True
            for line in lines:
                if onLine(line, x, y):
                    isBlack = not isBlack
                    pixels[x][y] = True

        if isBlack:
            print("an error has occured at x%sz%s"%(x,line[2]))


def findRelevantLines(lineList, x):
    for line in lineList:
        same = False
        above = False
        below = False
        for pt in line:
            if pt[0] > x:
                above = True
            elif pt[0] == x:
                same = True
            else:
                below = True
        if above and below:
            yield line
        elif same and above:
            yield line

def onLine(line, x, y):
    ratio = (x - line[0][0]) / (line[1][0] - line[0][0])
    ydist = line[1][1] - line[0][1]
    newy = line[0][1] + ratio*ydist
    xgood = False
    ygood = False
    if int(line[0][0]) == x or int(line[1][0]) == x or max(line[0][0], line[1][0]) >= x and min(line[0][0], line[1][0]) <= x:
        xgood = True
    if int(line[0][1]) == y or int(line[1][1]) == y or max(line[0][1], line[1][1]) >= y and min(line[0][1], line[1][1]) <= y:
        ygood = True
    if int(newy) == y and xgood and ygood:
        return True
    else:
        return False
