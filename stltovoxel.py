import argparse
import os
import io
import glob
import xml.etree.cElementTree as ET
import zipfile

from PIL import Image

import slice
import stl_reader


def doExport(inputFilePath, outputFilePath, resolution, pad, bounding_box=None):
    org_mesh = stl_reader.read_stl_verticies(inputFilePath)
    vol_mesh, scale, shift, bounding_box = slice.scaleAndShiftMesh(org_mesh, resolution)
    if scale == 0:
        print('Too small resolution: %d' % resolution)
        return

    vol, bounding_box = slice.meshToPlane(vol_mesh, bounding_box, pad)

    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)
    if outputFileExtension == '.png':
        exportPngs(vol, bounding_box, outputFilePath)
    elif outputFileExtension == '.xyz':
        exportXyz(vol, bounding_box, outputFilePath)
    elif outputFileExtension == '.svx':
        exportSvx(vol, bounding_box, outputFilePath, scale, shift)


def exportPngs(voxels, bounding_box, outputFilePath):
    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)

    # delete the previous output files
    fileList = glob.glob(outputFilePattern + '_*.png')
    for filePath in fileList:
        try:
            os.remove(filePath)
        except Exception:
            print("Error while deleting file : ", filePath)

    size = str(len(str(bounding_box[2]))+1)
    for height in range(bounding_box[2]):
        print('export png %d/%d' % (height, bounding_box[2]))
        img = Image.fromarray(voxels[height])
        path = (outputFilePattern + "_%0" + size + "d.png") % height
        img.save(path)


def exportXyz(voxels, bounding_box, outputFilePath):
    output = open(outputFilePath, 'w')
    for z in range(bounding_box[2]):
        for y in range(bounding_box[1]):
            for x in range(bounding_box[0]):
                if voxels[z][y][x]:
                    output.write('%s %s %s\n' % (x, y, z))
    output.close()


def exportSvx(voxels, bounding_box, outputFilePath, scale, shift):
    size = str(len(str(bounding_box[2]))+1)
    root = ET.Element("grid", attrib={"gridSizeX": str(bounding_box[0]),
                                      "gridSizeY": str(bounding_box[1]),
                                      "gridSizeZ": str(bounding_box[2]),
                                      "voxelSize": str(1.0/scale/1000),  # STL is probably in mm, and svx needs meters
                                      "subvoxelBits": "8",
                                      "originX": str(-shift[0]),
                                      "originY": str(-shift[1]),
                                      "originZ": str(-shift[2]),
                                      })
    manifest = ET.tostring(root)
    with zipfile.ZipFile(outputFilePath, 'w', zipfile.ZIP_DEFLATED) as zipFile:
        for height in range(bounding_box[2]):
            img = Image.fromarray(voxels[height])
            output = io.BytesIO()
            img.save(output, format="PNG")
            zipFile.writestr(("density/slice%0" + size + "d.png") % height, output.getvalue())
        zipFile.writestr("manifest.xml", manifest)


def file_choices(choices, fname):
    filename, ext = os.path.splitext(fname)
    if ext == '' or ext.lower() not in choices:
        if len(choices) == 1:
            parser.error('%s doesn\'t end with %s' % (fname, choices))
        else:
            parser.error('%s doesn\'t end with one of %s' % (fname, choices))
    return fname


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert STL files to voxels')
    parser.add_argument('input', nargs='?', type=lambda s: file_choices(('.stl', ), s), help='The input STL file')
    parser.add_argument(
        'output', nargs='?',
        type=lambda s: file_choices(('.png', '.xyz', '.svx'), s),
        help='path to output files. The export data type is chosen by file extension. Possible are .png, .xyz and .svx')
    parser.add_argument('resolution', nargs='?', type=int, default=100, help='number of voxels in both directions')
    parser.add_argument('pad', nargs='?', type=int, default=1, help='number of padding pixels')

    args = parser.parse_args()
    doExport(args.input, args.output, args.resolution, args.pad)
