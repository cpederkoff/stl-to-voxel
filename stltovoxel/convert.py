import glob
import os

import numpy as np
from PIL import Image, ImageOps
from stl import mesh

from . import slice


def convert_mesh(mesh, resolution=100, voxel_size=None, parallel=True):
    return convert_meshes([mesh], resolution, voxel_size, parallel)


def convert_meshes(meshes, resolution=100, voxel_size=None, parallel=True):
    mesh_min, mesh_max = slice.calculate_mesh_limits(meshes)
    scale, shift, shape = slice.calculate_scale_and_shift(
        mesh_min, mesh_max, resolution, voxel_size
    )
    vol = np.zeros(shape[::-1], dtype=np.int8)
    for mesh_ind, org_mesh in enumerate(meshes):
        slice.scale_and_shift_mesh(org_mesh, scale, shift)
        cur_vol = slice.mesh_to_plane(org_mesh, shape, parallel)
        vol[cur_vol] = mesh_ind + 1
    return vol, scale, shift


def convert_file(
    input_file_path,
    output_file_path,
    resolution=100,
    voxel_size=None,
    pad=1,
    parallel=False,
):
    convert_files(
        [input_file_path],
        output_file_path,
        resolution=resolution,
        voxel_size=voxel_size,
        pad=pad,
        parallel=parallel,
    )


def convert_files(
    input_file_paths,
    output_file_path,
    colors=[(255, 255, 255)],
    resolution=100,
    voxel_size=None,
    pad=1,
    parallel=False,
):
    meshes = []
    for input_file_path in input_file_paths:
        mesh_obj = mesh.Mesh.from_file(input_file_path)
        org_mesh = np.hstack(
            (
                mesh_obj.v0[:, np.newaxis],
                mesh_obj.v1[:, np.newaxis],
                mesh_obj.v2[:, np.newaxis],
            )
        )
        meshes.append(org_mesh)

    vol, scale, shift = convert_meshes(meshes, resolution, voxel_size, parallel)
    _output_file_pattern, output_file_extension = os.path.splitext(output_file_path)
    if output_file_extension == ".png":
        vol = np.pad(vol, pad)
        export_pngs(vol, output_file_path, colors)
    elif output_file_extension == ".xyz":
        export_xyz(vol, output_file_path, scale, shift)
    elif output_file_extension == ".npy":
        export_npy(vol, output_file_path, scale, shift)


def export_pngs(voxels, output_file_path, colors):
    output_file_pattern, _output_file_extension = os.path.splitext(output_file_path)

    # delete the previous output files
    file_list = glob.glob(output_file_pattern + "_*.png")
    for file_path in file_list:
        try:
            os.remove(file_path)
        except Exception:
            print("Error while deleting file : ", file_path)

    z_size = voxels.shape[0]

    size = str(len(str(z_size + 1)))
    # Black background
    colors = [(0, 0, 0)] + colors
    palette = [channel for color in colors for channel in color]
    for height in range(z_size):
        print("export png %d/%d" % (height, z_size))
        # Special case when white on black.
        if colors == [(0, 0, 0), (255, 255, 255)]:
            img = Image.fromarray(voxels[height].astype("bool"))
        else:
            img = Image.fromarray(voxels[height].astype("uint8"), mode="P")
            img.putpalette(palette)

        # Pillow puts (0,0) in the upper left corner, but 3D viewing coordinate systems put (0,0) in the lower left.
        # Fliping image vertically (top to bottom) makes the lower left corner (0,0) which is appropriate for this application.
        img = ImageOps.flip(img)
        path = (output_file_pattern + "_%0" + size + "d.png") % height
        img.save(path)


def export_xyz(voxels, output_file_path, scale, shift):
    points = _get_transformed_points(voxels, scale, shift)

    with open(output_file_path, "w") as output:
        for point in points:
            output.write("%s %s %s\n" % tuple(point))


def export_npy(voxels, output_file_path, scale, shift):
    points = _get_transformed_points(voxels, scale, shift)
    np.save(output_file_path, points)


def _get_transformed_points(voxels, scale, shift):
    voxels = voxels.astype(bool)
    true_coords = np.where(voxels)
    coords = np.vstack(true_coords).T
    coords = coords[:, [2, 1, 0]]
    return (coords / scale) + shift
