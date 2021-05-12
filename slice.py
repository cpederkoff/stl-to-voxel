import os
import math
import perimeter
import psutil
import ray
import numpy as np
from functools import reduce


def meshToPlane(mesh, bounding_box, pad):
    if os.getenv('DEBUG'):
        # https://groups.google.com/g/ray-dev/c/7euaVHZNhEw
        ray.init(local_mode=True)
    else:
        num_cpus = psutil.cpu_count(logical=False)
        ray.init(num_cpus=num_cpus)

    result_ids = []

    current_mesh_indices = set()
    z = 0
    for event_z, status, tri_ind in generateTriEvents(mesh):
        while event_z - z >= 0:
            mesh_subset = reduce(lambda acc, cur: acc + [mesh[cur]], current_mesh_indices, [])
            result_id = paintZplane.remote(mesh_subset, z, bounding_box[:2])
            result_ids.append(result_id)
            z += 1

        if status == 'start':
            assert tri_ind not in current_mesh_indices
            current_mesh_indices.add(tri_ind)
        elif status == 'end':
            assert tri_ind in current_mesh_indices
            current_mesh_indices.remove(tri_ind)
    print('ray.remote()')

    results = ray.get(result_ids)
    print('ray.get()')

    pad_bounding_box = [size + (pad * 2) for size in bounding_box]
    # Note: vol should be addressed with vol[z][y][x]
    vol = np.zeros(pad_bounding_box[::-1], dtype=bool)

    for z, pixels in results:
        vol[z+pad, pad:-pad, pad:-pad] = pixels
    print('build volume')

    ray.shutdown()
    return vol, pad_bounding_box


@ray.remote
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
    return p1 * (1-distance) + p2 * distance


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


def scaleAndShiftMesh(mesh, resolution):
    v_min = mesh.min(axis=(0, 1))
    v_max = mesh.max(axis=(0, 1))
    amplitude = v_max - v_min
    xy_scale = float(resolution - 1) / max(amplitude[:2])

    for i, shift in enumerate(v_min):
        mesh[..., i] = (mesh[..., i] - shift) * xy_scale

    z_resolution = amplitude[2] * xy_scale
    if z_resolution == math.ceil(z_resolution):
        z_resolution += 1
    else:
        z_resolution = math.ceil(z_resolution)
    bounding_box = [resolution, resolution, int(z_resolution)]

    return mesh, xy_scale, -v_min, bounding_box


def generateTriEvents(mesh):
    # Create data structure for plane sweep
    events = []
    for i, tri in enumerate(mesh):
        bottom, middle, top = sorted(tri, key=lambda pt: pt[2])
        events.append((bottom[2], 'start', i))
        events.append((top[2], 'end', i))
    return sorted(events, key=lambda tup: tup[0])
