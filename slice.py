import numpy as np
import math
import itertools
import perimeter


def slice(mesh, height, bounding_box):
    perim = toPerimeterLinesOrTriangles(mesh, height)
    return toVoxels(perim, bounding_box[0], bounding_box[1])


def toPerimeterLinesOrTriangles(mesh, height):
    relevantTriangles = list(filter(lambda tri: isAboveAndBelow(tri, height), mesh))
    return map(lambda tri: triangleToIntersectingLines(tri, height), relevantTriangles)





def lineToVoxels(line, pixels):
    p1 = line[0]
    p2 = line[1]
    drawLineOnPixels(p1, p2, pixels)


def toVoxels(pointList, x, y):
    # find all voxels that intersect any lines
    assert (pointList is not None)
    pixels = np.zeros((x, y), dtype=bool)
    perim = []
    for line in pointList:
        line = removeDupsFromPointList(line)
        if len(line) == 2:
            perim.append(line)
            lineToVoxels(line, pixels)
        elif len(line) == 3:
            triangleToVoxels(line, pixels)
    if len(perim) > 0:
        perimeter.fillPerimeter(removeDupsFromPointList(list(perim)), pixels)
    return pixels


def drawLineOnPixels(p1, p2, pixels):
    lineSteps = math.ceil(manhattanDistance(p1, p2))
    if lineSteps == 0:
        pixels[int(p1[0]), int(p2[1])] = True
        return
    for j in range(lineSteps + 1):
        point = linearInterpolation(p1, p2, j / lineSteps)
        pixels[int(point[0]), int(point[1])] = True

def triangleToVoxels(triangle, pixels):
    for (p1, p2) in itertools.combinations(triangle, 2):
        drawLineOnPixels(p1, p2, pixels)
    fill(triangle, pixels)

def fill(triangle, pixels):
    numSteps = math.ceil(max(manhattanDistance(triangle[0], triangle[2]), manhattanDistance(triangle[1], triangle[2])))
    for i in range(numSteps):
        p1 = linearInterpolation(triangle[0], triangle[2], i / numSteps)
        p2 = linearInterpolation(triangle[1], triangle[2], i / numSteps)
        drawLineOnPixels(p1, p2, pixels)

def roundList(l):
    if type(l) is list:
        ret = []
        for element in l:
            ret.append(roundList(element))
        return ret
    elif type(l) is tuple:
        ret = []
        for element in l:
            ret.append(roundList(element))
        return tuple(ret)
    else:
        return int(l)

def manhattanDistance(p1, p2, d=2):
    assert (len(p1) == len(p2))
    allDistances = 0
    for i in range(d):
        allDistances += abs(p1[i] - p2[i])
    return allDistances


def printBigArray(big, yes='1', no='0'):
    print()
    for line in big:
        for char in line:
            if char:
                print(yes, end=" ")
            else:
                print(no, end=" ")
        print()


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
    return (
        p1[0] - distance * slopex,
        p1[1] - distance * slopey,
        p1[2] - distance * slopez
    )


def isAboveAndBelow(pointList, height):
    '''

    :param pointList: Can be line or triangle
    :param height:
    :return: true if any line from the triangle crosses or is on the height line,
    '''
    above = list(filter(lambda pt: pt[2] > height, pointList))
    below = list(filter(lambda pt: pt[2] < height, pointList))
    same = list(filter(lambda pt: pt[2] == height, pointList))
    if len(same) == 3 or len(same) == 2:
        return True
    elif (above and below):
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
        return triangle
    elif len(same) == 2:
        return same[0], same[1]
    elif len(same) == 1:
        side1 = whereLineCrossesZ(above[0], below[0], height)
        return side1, same[0]
    else:
        lines = []
        for a in above:
            for b in below:
                lines.append((b, a))
        side1 = whereLineCrossesZ(lines[0][0], lines[0][1], height)
        side2 = whereLineCrossesZ(lines[1][0], lines[1][1], height)
        return side1, side2


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
    xyscale = float(resolution - 1) / (max(maxs[0] - mins[0], maxs[1] - mins[1]))
    scale = [xyscale, xyscale, xyscale]
    bounding_box = [resolution, resolution, math.ceil((maxs[2] - mins[2]) * xyscale)]
    return (scale, shift, bounding_box)


def scaleAndShiftMesh(mesh, scale, shift):
    for tri in mesh:
        newTri = []
        for pt in tri:
            newpt = [0, 0, 0]
            for i in range(3):
                newpt[i] = (pt[i] + shift[i]) * scale[i]
            newTri.append(tuple(newpt))
        if len(removeDupsFromPointList(newTri)) == 3:
            yield newTri
        else:
            pass


def removeDupsFromPointList(ptList):
    newList = ptList[:]
    return tuple(set(newList))

