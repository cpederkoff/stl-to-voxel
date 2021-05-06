import math

from util import removeDupsFromPointList


def toIntersectingLines(mesh, height):
    return list(filter(None, map(lambda tri: triangleToIntersectingLines(tri, height), mesh)))


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


def generateEvents(mesh):
    # Create data structure for plane sweep
    events = []
    for i, tri in enumerate(mesh):
        bottom, middle, top = sorted(tri, key=lambda pt: pt[2])
        events.append((bottom[2], 'start', i))
        events.append((top[2], 'end', i))
    return sorted(events, key=lambda tup: tup[0])


# Return a line segment of the triangle sliced at the given height.
def triangleToIntersectingLines(triangle, height):
    assert (len(triangle) == 3)
    above = list(filter(lambda pt: pt[2] > height, triangle))
    below = list(filter(lambda pt: pt[2] < height, triangle))
    same = list(filter(lambda pt: pt[2] == height, triangle))
    assert len(same) != 3
    if len(same) == 2:
        return same[0], same[1]
    elif len(same) == 1 and len(above) == 1 and len(below) == 1:
        side1 = whereLineCrossesZ(above[0], below[0], height)
        return side1, same[0]
    elif len(same) == 1:
        return None
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
    xyscale = (resolution - 1) / (max(maxs[0] - mins[0], maxs[1] - mins[1]))
    # TODO: Change this to return one scale. If not, verify svx exporting still works.
    scale = [xyscale, xyscale, xyscale]
    bounding_box = [resolution, resolution, math.ceil((maxs[2] - mins[2]) * xyscale) + 1]
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
