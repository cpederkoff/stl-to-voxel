import heapq
import numpy as np
import math
import itertools
import matplotlib.pyplot as plt


def slice(mesh, height, bounding_box):
    perim = toPerimeterLinesOrTriangles(mesh, height)
    return toVoxels(perim, bounding_box[0], bounding_box[1])


def toPerimeterLinesOrTriangles(mesh, height):
    relevantTriangles = list(filter(lambda tri: isAboveAndBelow(tri, height), mesh))
    intersectingLines = map(lambda tri: triangleToIntersectingLines(tri, height), relevantTriangles)
    for pair in intersectingLines:
        pair = list(pair)
        if len(pair[0]) == 2:
            yield map(lambda line: whereLineCrossesZ(line[0], line[1], height), pair)
        elif len(pair[0]) == 3:
            yield pair[0]


def triangleToVoxels(line, pixels, x, y):
    for (p1, p2) in itertools.combinations(line, 2):
        for i in range(x + y):
            newpoint = linearInterpolation(p1, p2, i / (x + y))
            # can replace with just int for spped increase. Decreases quality?
            pixels[int(newpoint[0]), int(newpoint[1])] = True
    fill(line, pixels)


def lineToVoxels(line, pixels, x, y):
    p1 = line[0]
    p2 = line[1]
    drawLineOnPixels(p1, p2, pixels)


def toVoxels(pointList, x, y):
    # find all voxels that intersect any lines
    assert (pointList != None)
    pixels = np.zeros((x, y), dtype=bool)
    for line in pointList:
        line = removeDupsFromPointList(line)
        if len(line) == 1:
            newpoint = line[0]
            pixels[int(newpoint[0]), int(newpoint[1])] = True
        elif len(line) == 2:
            lineToVoxels(line, pixels, x, y)
        elif len(line) == 3:
            triangleToVoxels(line, pixels, x, y)
        else:
            assert (False)
    return pixels


def drawLineOnPixels(p1, p2, pixels):
    lineSteps = math.ceil(manDistance(p1, p2))
    if lineSteps == 0:
        pixels[int(p1[0]), int(p2[1])] = True
        return
    for j in range(lineSteps + 1):
        point = linearInterpolation(p1, p2, j / lineSteps)
        pixels[int(point[0]), int(point[1])] = True


def fill(triangle, pixels):
    numSteps = max(manDistance(triangle[0], triangle[2]), manDistance(triangle[1], triangle[2]))
    for i in range(numSteps):
        p1 = linearInterpolation(triangle[0], triangle[2], i / numSteps)
        p2 = linearInterpolation(triangle[1], triangle[2], i / numSteps)
        drawLineOnPixels(p1, p2, pixels)


def manDistance(p1, p2, d=2):
    assert (len(p1) == len(p2))
    sum = 0
    for i in range(d):
        sum += abs(p1[i] - p2[i])
    return sum


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
    return [
        p1[0] - distance * slopex,
        p1[1] - distance * slopey,
        p1[2] - distance * slopez
    ]


def isAboveAndBelow(pointList, height):
    '''

    :param pointList: Can be line or triangle
    :param height:
    :return: true if at line from the triangle crosses or is on the height line,
    '''
    deltas = list(map(lambda pt: pt[2] - height, pointList))
    # if max(deltas) == 0 and min(deltas) == 0 and len(pointList) == 3:
    # #Unicorn case
    # print("unicorn", pointList, height)
    if max(deltas) >= 0 and min(deltas) <= 0:
        return True
    else:
        return False


def triangleToIntersectingLines(triangle, height):
    above = list(filter(lambda pt: pt[2] > height, triangle))
    below = list(filter(lambda pt: pt[2] < height, triangle))
    same = list(filter(lambda pt: pt[2] == height, triangle))
    assert (len(triangle) == 3)
    if len(same) == 3:
        # return a triangle if all is on the intersecting plane.
        yield triangle
    else:
        # return a line otherwise
        for aind in range(3):
            a = triangle[aind]
            for b in triangle[aind:]:
                if list(a) != list(b) and isAboveAndBelow((a, b), height):
                    if (a[2] > b[2]):
                        yield (b, a)
                    else:
                        yield (a, b)


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
    return linearInterpolation(p1, p2, distance)


def calculateScaleAndShift(mesh, resolution):
    allPoints = [item for sublist in mesh for item in sublist]
    mins = [0, 0, 0]
    maxs = [0, 0, 0]
    for i in range(3):
        mins[i] = min(allPoints, key=lambda tri: tri[i])[i]
        maxs[i] = max(allPoints, key=lambda tri: tri[i])[i]
    shift = [-min for min in mins]
    xyscale = float(resolution-1) / (max(maxs[0] - mins[0], maxs[1] - mins[1]))# + 0.0000001
    scale = [xyscale, xyscale, xyscale]
    bounding_box = [resolution, resolution, int(math.ceil((maxs[2] - mins[2]) * xyscale))]
    return (scale, shift, bounding_box)


def scaleAndShiftMesh(mesh, scale, shift):
    for tri in mesh:
        newTri = []
        for pt in tri:
            newpt = [0, 0, 0]
            for i in range(3):
                newpt[i] = int((pt[i] + shift[i]) * scale[i])
            newTri.append(newpt)
        yield newTri


def removeDupsFromPointList(ptList):
    newList = []
    for p in ptList:
        if p not in newList:
            newList.append(p)
    return newList

