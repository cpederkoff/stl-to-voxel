import io
import glob
import os
from PIL import Image, ImageOps
from stl import mesh
import xml.etree.cElementTree as ETree
import zipfile
import numpy as np

from . import slice


def convert_mesh(mesh, resolution=100, voxel_size=None, parallel=True):
    return convert_meshes([mesh], resolution, voxel_size, parallel)


def convert_meshes(meshes, resolution=100, voxel_size=None, parallel=True):
    mesh_min, mesh_max = slice.calculate_mesh_limits(meshes)
    scale, shift, shape = slice.calculate_scale_and_shift(mesh_min, mesh_max, resolution, voxel_size)
    vol = np.zeros(shape[::-1], dtype=np.int8)
    for mesh_ind, org_mesh in enumerate(meshes):
        slice.scale_and_shift_mesh(org_mesh, scale, shift)
        cur_vol = slice.mesh_to_plane(org_mesh, shape, parallel)
        vol[cur_vol] = mesh_ind + 1
    return vol, scale, shift


def convert_file(input_file_path, output_file_path, resolution=100, voxel_size=None, pad=1, parallel=False):
    convert_files([input_file_path], output_file_path, resolution=resolution,
                  voxel_size=voxel_size, pad=pad, parallel=parallel)


def convert_files(input_file_paths, output_file_path, colors=[(255, 255, 255)],
                  resolution=100, voxel_size=None, pad=1, parallel=False):
    meshes = []
    for input_file_path in input_file_paths:
        mesh_obj = mesh.Mesh.from_file(input_file_path)
        org_mesh = np.hstack((mesh_obj.v0[:, np.newaxis], mesh_obj.v1[:, np.newaxis], mesh_obj.v2[:, np.newaxis]))
        meshes.append(org_mesh)

    vol, scale, shift = convert_meshes(meshes, resolution, voxel_size, parallel)
    _output_file_pattern, output_file_extension = os.path.splitext(output_file_path)
    if output_file_extension == '.png':
        vol = np.pad(vol, pad)
        export_pngs(vol, output_file_path, colors)
    elif output_file_extension == '.xyz':
        export_xyz(vol, output_file_path, scale, shift)
    elif output_file_extension == '.svx':
        export_svx(vol, output_file_path, scale, shift)
    elif output_file_extension == '.npy':
        export_npy(vol, output_file_path, scale, shift)


def export_pngs(voxels, output_file_path, colors):
    output_file_pattern, _output_file_extension = os.path.splitext(output_file_path)

    # delete the previous output files
    file_list = glob.glob(output_file_pattern + '_*.png')
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
        print('export png %d/%d' % (height, z_size))
        # Special case when white on black.
        if colors == [(0, 0, 0), (255, 255, 255)]:
            img = Image.fromarray(voxels[height].astype('bool'))
        else:
            img = Image.fromarray(voxels[height].astype('uint8'), mode='P')
            img.putpalette(palette)

        # Pillow puts (0,0) in the upper left corner, but 3D viewing coordinate systems put (0,0) in the lower left.
        # Fliping image vertically (top to bottom) makes the lower left corner (0,0) which is appropriate for this application.
        img = ImageOps.flip(img)
        path = (output_file_pattern + "_%0" + size + "d.png") % height
        img.save(path)


def export_xyz(voxels, output_file_path, scale, shift):
    voxels = voxels.astype(bool)
    output = open(output_file_path, 'w')
    for z in range(voxels.shape[0]):
        for y in range(voxels.shape[1]):
            for x in range(voxels.shape[2]):
                if voxels[z][y][x]:
                    point = (np.array([x, y, z]) / scale) + shift
                    output.write('%s %s %s\n' % tuple(point))
    output.close()


def export_npy(voxels, output_file_path, scale, shift):
    voxels = voxels.astype(bool)
    out = []
    for z in range(voxels.shape[0]):
        for y in range(voxels.shape[1]):
            for x in range(voxels.shape[2]):
                if voxels[z][y][x]:
                    point = (np.array([x, y, z]) / scale) + shift
                    out.append(point)
    np.save(output_file_path, out)


def export_svx(voxels, output_file_path, scale, shift):
    # Collapse all materials into one
    voxels = voxels.astype(bool)
    z_size, y_size, x_size = voxels.shape
    size = str(len(str(z_size))+1)
    root = ETree.Element("grid", attrib={"gridSizeX": str(x_size),
                                         "gridSizeY": str(y_size),
                                         "gridSizeZ": str(z_size),
                                         "voxelSize": str(1.0/scale/1000),  # STL is probably in mm, and svx needs meters
                                         "subvoxelBits": "8",
                                         "originX": str(shift[0]),
                                         "originY": str(shift[1]),
                                         "originZ": str(shift[2]),
                                         })
    manifest = ETree.tostring(root)
    with zipfile.ZipFile(output_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for height in range(z_size):
            img = Image.fromarray(voxels[height])
            img = ImageOps.flip(img)
            output = io.BytesIO()
            img.save(output, format="PNG")
            zip_file.writestr(("density/slice%0" + size + "d.png") % height, output.getvalue())
        zip_file.writestr("manifest.xml", manifest)
