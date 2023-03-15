import numpy as np
import multiprocessing as mp
import pdb

from . import perimeter


def mesh_to_plane(mesh, bounding_box, parallel):
    if parallel:
        pool = mp.Pool(mp.cpu_count())
        result_ids = []

    # Note: vol should be addressed with vol[z][y][x]
    vol = np.zeros(bounding_box[::-1], dtype=bool)
    current_mesh_indices = set()
    z = 0
    for event_z, status, tri_ind in generate_tri_events(mesh):
        while event_z - z >= 0:
            mesh_subset = [mesh[ind] for ind in current_mesh_indices]
            if parallel:
                result_id = pool.apply_async(paint_z_plane, args=(mesh_subset, z, vol.shape[1:]))
                result_ids.append(result_id)
            else:
                _, pixels = paint_z_plane(mesh_subset, z, vol.shape[1:])
                vol[z] = pixels
            z += 1

        if status == 'start':
            assert tri_ind not in current_mesh_indices
            current_mesh_indices.add(tri_ind)
        elif status == 'end':
            assert tri_ind in current_mesh_indices
            current_mesh_indices.remove(tri_ind)

    if parallel:
        results = [r.get() for r in result_ids]

        for z, pixels in results:
            vol[z] = pixels

        pool.close()
        pool.join()

    return vol


def paint_z_plane(mesh, height, plane_shape):
    print('Processing layer %d' % (height))

    pixels = np.zeros(plane_shape, dtype=bool)

    lines = []
    for triangle in mesh:
        points = triangle_to_intersecting_points(triangle, height)
        if len(points) == 1:
            pt = points[0]
            x,y,_ = pt
            x = int(x)
            y = int(y)
            pixels[y][x] = True
        if len(points) == 2:
            lines.append(tuple(points))
        if len(points) == 3:
            for i in range(3):
                pt = points[i]
                pt2 = points[(i+1)%3]
                lines.append((pt, pt2))
    perimeter.repaired_lines_to_voxels(lines, pixels)

    return height, pixels


def linear_interpolation(p1, p2, distance):
    '''
    :param p1: Point 1
    :param p2: Point 2
    :param distance: Between 0 and 1, Lower numbers return points closer to p1.
    :return: A point on the line between p1 and p2
    '''
    return p1 * (1-distance) + p2 * distance


def triangle_to_intersecting_points(triangle, height):
    assert (len(triangle) == 3)
    points = []
    # Find the pt index with the greatest z, start there
    start_index = max(range(3), key=lambda i: triangle[i][2])
    if triangle[(start_index+1)%3][2] == height:
        # Corner-case where there is a tie for highest point. 
        # The later point in the rotation should be chosen
        start_index = (start_index+1)%3
    for i in range(start_index, start_index + 3):
        pt = triangle[i%3]
        pt2 = triangle[(i+1)%3]
        if pt[2] == height:
            points.append(pt)
        elif (pt[2] < height and pt2[2] > height) or (pt[2] > height and pt2[2] < height):
            intersection = where_line_crosses_z(pt, pt2, height)
            points.append(intersection)
    
    return points

def where_line_crosses_z(p1, p2, z):
    if (p1[2] > p2[2]):
        p1, p2 = p2, p1
    # now p1 is below p2 in z
    if p2[2] == p1[2]:
        distance = 0
    else:
        distance = (z - p1[2]) / (p2[2] - p1[2])
    return linear_interpolation(p1, p2, distance)


def calculate_scale_shift(meshes, resolution, voxel_size):
    mesh_min = meshes[0].min(axis=(0, 1))
    mesh_max = meshes[0].max(axis=(0, 1))
    for mesh in meshes[1:]:
        mesh_min = np.minimum(mesh_min, mesh.min(axis=(0, 1)))
        mesh_max = np.maximum(mesh_max, mesh.max(axis=(0, 1)))

    bounding_box = mesh_max - mesh_min
    if voxel_size is not None:
        resolution = bounding_box / voxel_size
    else:
        if isinstance(resolution, int):
            resolution = resolution * bounding_box / bounding_box[2]
        else:
            resolution = np.array(resolution)

    scale = (resolution - 1) / bounding_box
    new_resolution = np.floor(resolution).astype(int) + 1
    return scale, mesh_min, new_resolution


def scale_and_shift_mesh(mesh, scale, shift):
    for i in range(3):
        mesh[..., i] = (mesh[..., i] - shift[i]) * scale[i]


def generate_tri_events(mesh):
    # Create data structure for plane sweep
    events = []
    for i, tri in enumerate(mesh):
        bottom, middle, top = sorted(tri, key=lambda pt: pt[2])
        events.append((bottom[2], 'start', i))
        events.append((top[2], 'end', i))
    return sorted(events, key=lambda tup: tup[0])
