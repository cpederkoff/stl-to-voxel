import heapq
import numpy as np
import math
import itertools
import matplotlib.pyplot as plt


def slice(mesh,height, bounding_box):
    perim = toPerimeterLinesOrTriangles(mesh,height)
    return toVoxels(perim, bounding_box[0], bounding_box[1])

def toPerimeterLinesOrTriangles(mesh,height):
    relevantTriangles = list(filter(lambda tri:isAboveAndBelow(tri,height), mesh))
    intersectingLines = map(lambda tri:triangleToIntersectingLines(tri,height),relevantTriangles)
    for pair in intersectingLines:
        pair = list(pair)
        if len(pair[0]) == 2:
            yield map(lambda line:whereLineCrossesZ(line[0],line[1],height),pair)
        elif len(pair[0]) == 3:
            yield pair[0]


def triangleToVoxels(line, pixels, x, y):
    for (p1, p2) in itertools.combinations(line, 2):
        for i in range(x + y):
            newpoint = linearInterpolation(p1, p2, i / (x + y))
            # can replace with just int for spped increase. Decreases quality?
            pixels[int(newpoint[0]), int(newpoint[1])] = True
    avg = [0, 0]
    for pt in line:
        avg[0] += pt[0]
        avg[1] += pt[1]
    avg[0] = int(round(avg[0] / 3))
    avg[1] = int(round(avg[1] / 3))
    # line2 = [[l[0],l[1]] for l in line]
    fill(avg, pixels)


def lineToVoxels(line, pixels, x, y):
    p1 = line[0]
    p2 = line[1]
    for i in range(x + y):
        newpoint = linearInterpolation(p1, p2, i / (x + y))
        # can replace with just int for spped increase. Decreases quality?
        pixels[int(newpoint[0]), int(newpoint[1])] = True


def toVoxels(pointList, x, y):
    #find all voxels that intersect any lines
    assert(pointList!=None)
    pixels = np.zeros((x, y), dtype=bool)
    for line in pointList:
        line = removeDupsFromPointList(line)
        if len(line) == 1:
            newpoint = line[0]
            pixels[int(newpoint[0]),int(newpoint[1])] = True
        elif len(line) == 2:
            lineToVoxels(line, pixels, x, y)
        elif len(line) == 3:
            triangleToVoxels(line, pixels, x, y)
        else:
            assert(False)
    return pixels

def fill(start, pixels):
    def getnearby(x,y):
        if x >= pixels.shape[0] or x < 0 or y >= pixels.shape[1] or y < 0:
            return
        for i in [[1,0],[0,1],[-1,0],[0,-1]]:
            yield (x+i[0],y+i[1])
    stack = []
    if not pixels[start[0],start[1]]:
        stack.append(start)
    while len(stack) > 0:
        x,y = heapq.heappop(stack)
        if not pixels[x,y]:
            near = list(getnearby(x,y))
            for n in near:
                heapq.heappush(stack, n)
            pixels[x,y] = True


def printBigArray(big, yes='1', no='0'):
    print()
    for line in big:
        for char in line:
            if char:
                print(yes, end=" ")
            else:
                print(no, end=" ")
        print()

def makeBigArrayOfZeros(n):
    big = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(' ')
        big.append(row)
    return big

def linearInterpolation(p1, p2, distance):
    '''
    :param p1: Point 1
    :param p2: Point 2
    :param distance: Between 0 and 1, Lower numbers return points closer to p1.
    :return: A point on the line between p1 and p2
    '''
    slopex = (p1[0] - p2[0])
    slopey = (p1[1] - p2[1])
    slopez = p1[2] - p2[2]
    return  [
        p1[0] - distance*slopex,
        p1[1] - distance*slopey,
        p1[2] - distance*slopez
    ]



def isAboveAndBelow(pointList,height):
    '''

    :param pointList: Can be line or triangle
    :param height:
    :return: true if at line from the triangle crosses or is on the height line,
    '''
    deltas = list(map(lambda pt:pt[2] - height, pointList))
    # if max(deltas) == 0 and min(deltas) == 0 and len(pointList) == 3:
    #     #Unicorn case
    #     print("unicorn", pointList, height)
    if max(deltas) >= 0 and min(deltas) <= 0:
        return True
    else:
        return False


def triangleToIntersectingLines(triangle,height):

    above = list(filter(lambda pt:pt[2]>height, triangle))
    below = list(filter(lambda pt:pt[2]<height, triangle))
    same = list(filter(lambda pt:pt[2]==height, triangle))
    assert(len(triangle) == 3)
    if len(same) == 3:
        #return a triangle if all is on the intersecting plane.
        yield triangle
    else:
        #return a line otherwise
        for aind in range(3):
            a = triangle[aind]
            for b in triangle[aind:]:
                if list(a) != list(b) and isAboveAndBelow((a,b), height):
                    if (a[2] > b[2]):
                        yield(b,a)
                    else:
                        yield(a,b)


def whereLineCrossesZ(p1, p2, z):
    if (p1[2] > p2[2]):
        t = p1
        p1 = p2
        p2 = t
    # now p1 is below p2 in z
    if p2[2] == p1[2]:
        distance = 0
    else:
        distance = (z - p1[2]) / (p2[2] - p1[2])
    return linearInterpolation(p1,p2,distance)

def calculateScaleAndShift(mesh, resolution):
    allPoints = [item for sublist in mesh for item in sublist]
    mins = [0,0,0]
    maxs = [0,0,0]
    for i in range(3):
        mins[i] = min(allPoints, key=lambda tri:tri[i])[i]
        maxs[i] = max(allPoints, key=lambda tri:tri[i])[i]
    shift = [-min for min in mins]
    xyscale = float(resolution)/(max(maxs[0]-mins[0], maxs[1] - mins[1]))+0.0000001
    scale = [xyscale,xyscale,xyscale]
    bounding_box = [int(math.ceil((maxs[i]-mins[i])*xyscale)) for i in range(3)]
    return (scale, shift, bounding_box)

def scaleAndShiftMesh(mesh, scale, shift):
    for tri in mesh:
        newTri = []
        for pt in tri:
            newpt = [0,0,0]
            for i in range(3):
                newpt[i] = int((pt[i] + shift[i])*scale[i])
            newTri.append(newpt)
        yield newTri

def removeDupsFromPointList(ptList):
    newList = []
    for p in ptList:
        if p not in newList:
            newList.append(p)
    return newList

