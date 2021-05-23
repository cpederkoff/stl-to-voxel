import argparse
import io
import glob
import os
from PIL import Image
from stl import mesh
import xml.etree.cElementTree as ETree
import zipfile
import numpy as np

from . import slice


def convert_mesh(mesh, resolution=100, pad=1, parallel=True):
    vol_mesh, scale, shift, bounding_box = slice.scale_and_shift_mesh(mesh, resolution)
    if scale == 0:
        print('Too small resolution: %d' % resolution)
        return

    vol, _bounding_box = slice.mesh_to_plane(vol_mesh, bounding_box, pad, parallel)
    return vol


def convert_file(input_file_path, output_file_path, resolution=100, pad=1, parallel=False):
    mesh_obj = mesh.Mesh.from_file(input_file_path)
    org_mesh = np.hstack((mesh_obj.v0[:, np.newaxis], mesh_obj.v1[:, np.newaxis], mesh_obj.v2[:, np.newaxis]))
    vol_mesh, scale, shift, bounding_box = slice.scale_and_shift_mesh(org_mesh, resolution)
    if scale == 0:
        print('Too small resolution: %d' % resolution)
        return

    vol, bounding_box = slice.mesh_to_plane(vol_mesh, bounding_box, pad, parallel)

    output_file_pattern, output_file_extension = os.path.splitext(output_file_path)
    if output_file_extension == '.png':
        export_pngs(vol, bounding_box, output_file_path)
    elif output_file_extension == '.xyz':
        export_xyz(vol, bounding_box, output_file_path)
    elif output_file_extension == '.svx':
        export_svx(vol, bounding_box, output_file_path, scale, shift)


def export_pngs(voxels, bounding_box, output_file_path):
    output_file_pattern, output_file_extension = os.path.splitext(output_file_path)

    # delete the previous output files
    file_list = glob.glob(output_file_pattern + '_*.png')
    for file_path in file_list:
        try:
            os.remove(file_path)
        except Exception:
            print("Error while deleting file : ", file_path)

    size = str(len(str(bounding_box[2] + 1)))
    for height in range(bounding_box[2]):
        print('export png %d/%d' % (height, bounding_box[2]))
        img = Image.fromarray(voxels[height])
        path = (output_file_pattern + "_%0" + size + "d.png") % height
        img.save(path)


def export_xyz(voxels, bounding_box, output_file_path):
    output = open(output_file_path, 'w')
    for z in range(bounding_box[2]):
        for y in range(bounding_box[1]):
            for x in range(bounding_box[0]):
                if voxels[z][y][x]:
                    output.write('%s %s %s\n' % (x, y, z))
    output.close()


def export_svx(voxels, bounding_box, output_file_path, scale, shift):
    size = str(len(str(bounding_box[2]))+1)
    root = ETree.Element("grid", attrib={"gridSizeX": str(bounding_box[0]),
                                         "gridSizeY": str(bounding_box[1]),
                                         "gridSizeZ": str(bounding_box[2]),
                                         "voxelSize": str(1.0/scale/1000),  # STL is probably in mm, and svx needs meters
                                         "subvoxelBits": "8",
                                         "originX": str(-shift[0]),
                                         "originY": str(-shift[1]),
                                         "originZ": str(-shift[2]),
                                         })
    manifest = ETree.tostring(root)
    with zipfile.ZipFile(output_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for height in range(bounding_box[2]):
            img = Image.fromarray(voxels[height])
            output = io.BytesIO()
            img.save(output, format="PNG")
            zip_file.writestr(("density/slice%0" + size + "d.png") % height, output.getvalue())
        zip_file.writestr("manifest.xml", manifest)


def file_choices(parser, choices, fname):
    filename, ext = os.path.splitext(fname)
    if ext == '' or ext.lower() not in choices:
        if len(choices) == 1:
            parser.error('%s doesn\'t end with %s' % (fname, choices))
        else:
            parser.error('%s doesn\'t end with one of %s' % (fname, choices))
    return fname


def main():
    parser = argparse.ArgumentParser(description='Convert STL files to voxels')
    parser.add_argument('input', type=lambda s: file_choices(parser, ('.stl'), s), help='Input STL file')
    parser.add_argument(
        'output',
        type=lambda s: file_choices(parser, ('.png', '.xyz', '.svx'), s),
        help='Path to output files. The export data type is chosen by file extension. Possible are .png, .xyz and .svx')
    parser.add_argument('--resolution', type=int, default=100, help='Number of voxels in both directions')
    parser.add_argument('--pad', type=int, default=1, help='Number of padding pixels')
    parser.add_argument('--no-parallel', dest='parallel', action='store_false', help='Disable parallel processing')
    parser.set_defaults(parallel=True)

    args = parser.parse_args()
    convert_file(args.input, args.output, args.resolution, args.pad, args.parallel)


if __name__ == '__main__':
    main()
