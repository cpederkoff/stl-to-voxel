import argparse
import os.path
import io
import xml.etree.cElementTree as ET
from zipfile import ZipFile
import zipfile

from PIL import Image
import numpy as np

import slice
import stl_reader
import perimeter
from util import arrayToWhiteGreyscalePixel, padVoxelArray


def doExport(inputFilePath, outputFilePath, resolution):
    mesh = list(stl_reader.read_stl_verticies(inputFilePath))
    (scale, shift, bounding_box) = slice.calculateScaleAndShift(mesh, resolution)
    mesh = list(slice.scaleAndShiftMesh(mesh, scale, shift))
    # Note: vol should be addressed with vol[z][x][y]
    vol = np.zeros((bounding_box[2], bounding_box[0], bounding_box[1]), dtype=bool)

    events = slice.generateEvents(mesh)

    current_triangle_indecies = set()

    slice_height = -1
    for (z, status, tri_ind) in events:
        while z - slice_height >= 1:
            slice_height += 1
            print('Processing layer %d/%d' % (slice_height+1, bounding_box[2]))
            prepixel = np.zeros((bounding_box[0], bounding_box[1]), dtype=bool)
            mesh_subset = []
            for index in current_triangle_indecies:
                mesh_subset.append(mesh[index])
            lines = slice.toIntersectingLines(mesh_subset, slice_height, prepixel)
            perimeter.linesToVoxels(lines, prepixel)
            vol[slice_height] = prepixel

        if status == 'start':
            assert tri_ind not in current_triangle_indecies
            current_triangle_indecies.add(tri_ind)
        elif status == 'end':
            assert tri_ind in current_triangle_indecies
            current_triangle_indecies.remove(tri_ind)

    vol, bounding_box = padVoxelArray(vol)
    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)
    if outputFileExtension == '.png':
        exportPngs(vol, bounding_box, outputFilePath)
    elif outputFileExtension == '.xyz':
        exportXyz(vol, bounding_box, outputFilePath)
    elif outputFileExtension == '.svx':
        exportSvx(vol, bounding_box, outputFilePath, scale, shift)


def exportPngs(voxels, bounding_box, outputFilePath):
    size = str(len(str(bounding_box[2]))+1)
    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)
    for height in range(bounding_box[2]):
        img = Image.new('L', (bounding_box[0], bounding_box[1]), 'black')  # create a new black image
        pixels = img.load()
        arrayToWhiteGreyscalePixel(voxels[height], pixels)
        path = (outputFilePattern + "%0" + size + "d.png") % height
        img.save(path)


def exportXyz(voxels, bounding_box, outputFilePath):
    output = open(outputFilePath, 'w')
    for z in range(bounding_box[2]):
        for x in range(bounding_box[0]):
            for y in range(bounding_box[1]):
                if voxels[z][x][y]:
                    output.write('%s %s %s\n' % (x, y, z))
    output.close()


def exportSvx(voxels, bounding_box, outputFilePath, scale, shift):
    size = str(len(str(bounding_box[2]))+1)
    root = ET.Element("grid", attrib={"gridSizeX": str(bounding_box[0]),
                                      "gridSizeY": str(bounding_box[2]),
                                      "gridSizeZ": str(bounding_box[1]),
                                      "voxelSize": str(1.0/scale[0]/1000), #STL is probably in mm, and svx needs meters
                                      "subvoxelBits": "8",
                                      "originX": str(-shift[0]),
                                      "originY": str(-shift[2]),
                                      "originZ": str(-shift[1]),
                                      })
    channels = ET.SubElement(root, "channels")
    channel = ET.SubElement(channels, "channel", attrib={
        "type": "DENSITY",
        "slices": "density/slice%0" + size + "d.png"
    })
    manifest = ET.tostring(root)
    with ZipFile(outputFilePath, 'w', zipfile.ZIP_DEFLATED) as zipFile:
        for height in range(bounding_box[2]):
            img = Image.new('L', (bounding_box[0], bounding_box[1]), 'black')  # create a new black image
            pixels = img.load()
            arrayToWhiteGreyscalePixel(voxels[height], pixels)
            output = io.BytesIO()
            img.save(output, format="PNG")
            zipFile.writestr(("density/slice%0" + size + "d.png") % height, output.getvalue())
        zipFile.writestr("manifest.xml",manifest)


def file_choices(choices,fname):
    filename, ext = os.path.splitext(fname)
    if ext == '' or ext not in choices:
        if len(choices) == 1:
            parser.error('%s doesn\'t end with %s' % (fname, choices))
        else:
            parser.error('%s doesn\'t end with one of %s' % (fname, choices))
    return fname

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert STL files to voxels')
    parser.add_argument('input', nargs='?', type=lambda s: file_choices(('.stl', ), s), help='The input STL file')
    parser.add_argument('output', nargs='?', type=lambda s: file_choices(('.png', '.xyz', '.svx'), s), help='path to output files. The export data type is chosen by file extension. Possible are .png, .xyz and .svx')
    parser.add_argument('resolution', nargs='?', type=int, default=100, help='number of voxels in both directions')

    args = parser.parse_args()
    doExport(args.input, args.output, args.resolution)
