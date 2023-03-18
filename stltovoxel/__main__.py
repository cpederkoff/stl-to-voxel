import argparse
import os
from PIL import ImageColor

from .convert import convert_files


def file_choices(parser, choices, fname):
    _filename, ext = os.path.splitext(fname)
    if ext == '' or ext.lower() not in choices:
        if len(choices) == 1:
            parser.error('%s doesn\'t end with %s' % (fname, choices))
        else:
            parser.error('%s doesn\'t end with one of %s' % (fname, choices))
    return fname


def main():
    parser = argparse.ArgumentParser(description='Convert STL files to voxels')
    parser.add_argument('input', nargs='+', type=lambda s: file_choices(parser, ('.stl'), s), help='Input STL file')
    parser.add_argument(
        'output',
        type=lambda s: file_choices(parser, ('.png', '.npy', '.svx', '.xyz'), s),
        help='Path to output files. The export data type is chosen by file extension. Possible are .png, .xyz and .svx')
    parser.add_argument('--pad', type=int, default=1, help='Number of padding pixels. Only used during .png output.')
    parser.add_argument('--no-parallel', dest='parallel', action='store_false', help='Disable parallel processing')
    parser.add_argument('--colors', type=str, default="#FFFFFF", help='Output png colors. Ex red,#FF0000')
    # Only one resolution or size argument may be set
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--resolution', type=int, default=100, help='Number of voxels in z direction')
    group.add_argument('--resolution-xyz', type=int, nargs=3, dest='resolution',
                       help='Number of voxels in x, y, and z direction.')
    group.add_argument('--voxel-size', type=float, dest='voxel_size', help='Size of voxel in all dimensions')
    group.add_argument('--voxel-size-xyz', type=float, nargs=3, dest='voxel_size',
                       help='Size of voxel in xyz dimensions')

    parser.set_defaults(parallel=True)

    args = parser.parse_args()
    colors = args.colors.split(",")
    if os.path.splitext(args.output)[1] == '.png' and len(colors) < len(args.input):
        raise argparse.ArgumentTypeError('Must specify enough colors')

    color_tuples = [ImageColor.getcolor(color, "RGB") for color in colors]

    convert_files(args.input, args.output, color_tuples, args.resolution, args.voxel_size, args.pad, args.parallel)


if __name__ == '__main__':
    main()
