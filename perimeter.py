import math
from UnionFind import UnionFind
import poly_tri
from collections import defaultdict
import matplotlib.pyplot as plt


def orderIntoPerimeter(lineList):
    matcher = defaultdict(list)

    for p1,p2 in lineList:
        p1 = tuple(p1)
        p2 = tuple(p2)
        if p2 in matcher[p1]:
            matcher[p1].remove(p2)
        else:
            matcher[p1].append(p2)
        if p1 in matcher[p2]:
            matcher[p2].remove(p1)
        else:
            matcher[p2].append(p1)

    perimeter = []
    start = p1
    next = p2
    perimeter.append(next)
    matcher[start].remove(next)
    matcher[next].remove(start)
    while next != start:
        if len(matcher[next]) == 0:
            import pylab as pl

            pl.plot(next[0],next[1])
            print(next)
            x = []
            y = []
            for p1 in perimeter:
                x.append(p1[0])
                y.append(p1[1])
            pl.plot(x,y )
            pl.show()
        nextnext = matcher[next][0]
        perimeter.append(nextnext)
        matcher[nextnext].remove(next)
        matcher[next].remove(nextnext)
        next = nextnext
    return perimeter

def fillPerimeter(lineList, pixels):
    for x in range(len(pixels)):
        isBlack = False
        lines = list(findRelevantLines(lineList, x))
        lines = sanitizeLines(lines)
        # if x == 29:
        #     for line in lines:
        #         plt.plot([line[0][0],line[1][0]],[line[0][1],line[1][1]])
        #     plt.plot([x,x],[0,128],'g')
        #     plt.show()
        #     pass

        for y in range(len(pixels[x])):
            if y == 129:
                pass
            if isBlack:
                pixels[x][y] = True
            for line in lines:
                if onLine(line, x, y):
                    isBlack = not isBlack
                    pixels[x][y] = True

        if isBlack:
            #we know an error has occured
            print(lineList)
            print(lines)
            for line in lines:
                plt.plot([line[0][0],line[1][0]],[line[0][1],line[1][1]])
            plt.plot([x,x],[0,128],'g')
            plt.show()
            pass

def sanitizeLines(lineList):
    newlist = []
    for line in lineList:
        line = orderPoints(line)
        if line not in newlist:
            newlist.append(line)
    return newlist

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
    else\
            :
        return False


def separatePerimeters(lineList):
    uf = UnionFind()
    for p1,p2 in lineList:
        p1 = tuple(p1)
        p2 = tuple(p2)
        uf.union(p1,p2)
    perims = defaultdict(list)
    for line in lineList:
        group = uf[line[0]]
        perims[group].append(line)
    return list(perims.values())



def distance(p1, p2):
    assert (len(p1) == len(p2))
    allDistances = 0
    for i in range(len(p1)):
        allDistances += (p1[i] - p2[i])**2
    return math.sqrt(allDistances)

def triangulatePerimeter(lineList):
    triangles = []
    unorderedPerimeters = separatePerimeters(lineList)
    for unorderedPerim in unorderedPerimeters:
        perimeter = orderIntoPerimeter(unorderedPerim)
        triangles.extend(triangulate(perimeter))
    return triangles


def triangulate(perim):
    tris = []
    def callback(v1,v2,v3,*args):
        tris.append([v1,v2,v3])
    poly_tri.draw_poly(perim,callback)
    return tris

def orderPoints(line):
    p1,p2 = line
    if p1[0] < p2[0]:
        return [p1,p2]
    elif p2[0] < p1[0]:
        return [p2,p1]
    elif p1[1] < p2[1]:
        return [p1,p2]
    elif p2[1] < p1[1]:
        return [p2,p1]
    else:
        return [p1,p2]