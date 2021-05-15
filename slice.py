import math
import perimeter
import numpy as np
import multiprocessing as mp


def meshToPlane(mesh, bounding_box, pad):
    pool = mp.Pool(mp.cpu_count())

    result_ids = []

    current_mesh_indices = set()
    z = 0
    for event_z, status, tri_ind in generateTriEvents(mesh):
        while event_z - z >= 0:
            mesh_subset = [mesh[ind] for ind in current_mesh_indices]
            result_id = pool.apply_async(paintZplane, args=(mesh_subset, z, bounding_box[:2]))
            result_ids.append(result_id)
            z += 1

        if status == 'start':
            assert tri_ind not in current_mesh_indices
            current_mesh_indices.add(tri_ind)
        elif status == 'end':
            assert tri_ind in current_mesh_indices
            current_mesh_indices.remove(tri_ind)

    results = [r.get() for r in result_ids]

    pad_bounding_box = [size + (pad * 2) for size in bounding_box]
    # Note: vol should be addressed with vol[z][y][x]
    vol = np.zeros(pad_bounding_box[::-1], dtype=bool)

    for z, pixels in results:
        vol[z+pad, pad:-pad, pad:-pad] = pixels
    print('build volume')

    pool.close()
    pool.join()
    return vol, pad_bounding_box


def paintZplane(mesh, height, plane_shape):
    pixels = np.zeros(plane_shape, dtype=bool)

    lines = []
    for triangle in mesh:
        triangleToIntersectingLines(triangle, height, pixels, lines)
    perimeter.linesToVoxels(lines, pixels)

    return height, pixels


def linearInterpolation(p1, p2, distance):
    '''
    :param p1: Point 1
    :param p2: Point 2
    :param distance: Between 0 and 1, Lower numbers return points closer to p1.
    :return: A point on the line between p1 and p2
    '''
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    slopex = x1 - x2
    slopey = y1 - y2
    slopez = z1 - z2
    return (
        x1 - distance * slopex,
        y1 - distance * slopey,
        z1 - distance * slopez
    )


def triangleToIntersectingLines(triangle, height, pixels, lines):
    assert (len(triangle) == 3)
    above = list(filter(lambda pt: pt[2] > height, triangle))
    below = list(filter(lambda pt: pt[2] < height, triangle))
    same = list(filter(lambda pt: pt[2] == height, triangle))
    if len(same) == 3:
        for i in range(0, len(same) - 1):
            for j in range(i + 1, len(same)):
                lines.append((same[i], same[j]))
    elif len(same) == 2:
        lines.append((same[0], same[1]))
    elif len(same) == 1:
        if above and below:
            side1 = whereLineCrossesZ(above[0], below[0], height)
            lines.append((side1, same[0]))
        else:
            x = int(same[0][0])
            y = int(same[0][1])
            pixels[y][x] = True
    else:
        crossLines = []
        for a in above:
            for b in below:
                crossLines.append((b, a))
        side1 = whereLineCrossesZ(crossLines[0][0], crossLines[0][1], height)
        side2 = whereLineCrossesZ(crossLines[1][0], crossLines[1][1], height)
        lines.append((side1, side2))


def whereLineCrossesZ(p1, p2, z):
    if (p1[2] > p2[2]):
        p1, p2 = p2, p1
    # now p1 is below p2 in z
    if p2[2] == p1[2]:
        distance = 0
    else:
        distance = (z - p1[2]) / (p2[2] - p1[2])
    return linearInterpolation(p1, p2, distance)


def calculateMinMax(mesh):
    allPoints = [point for tri in mesh for point in tri]
    mins = [0, 0, 0]
    maxs = [0, 0, 0]
    for i in range(3):
        mins[i] = min(allPoints, key=lambda tri: tri[i])[i]
        maxs[i] = max(allPoints, key=lambda tri: tri[i])[i]

    for i, axis in enumerate(['x', 'y', 'z']):
        print(f'{axis}: {mins[i]} ~ {maxs[i]}')
    return mins, maxs


def calculateScaleAndShift(mesh, resolution):
    mins, maxs = calculateMinMax(mesh)
    shift = [-min for min in mins]
    xyscale = float(resolution - 1) / (max(maxs[0] - mins[0], maxs[1] - mins[1]))
    # TODO: Change this to return one scale. If not, verify svx exporting still works.
    scale = [xyscale, xyscale, xyscale]
    z_resolution = (maxs[2] - mins[2]) * xyscale
    if z_resolution == math.ceil(z_resolution):
        z_resolution += 1
    else:
        z_resolution = math.ceil(z_resolution)
    bounding_box = [resolution, resolution, int(z_resolution)]
    return (scale, shift, bounding_box)


def scaleAndShiftMesh(mesh, scale, shift):
    mesh = np.array(mesh)
    return (mesh + shift) * scale


def generateTriEvents(mesh):
    # Create data structure for plane sweep
    events = []
    for i, tri in enumerate(mesh):
        bottom, middle, top = sorted(tri, key=lambda pt: pt[2])
        events.append((bottom[2], 'start', i))
        events.append((top[2], 'end', i))
    return sorted(events, key=lambda tup: tup[0])
