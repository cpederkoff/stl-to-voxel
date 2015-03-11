import argparse
from PIL import Image
import numpy as np
import os.path

import slice
import stl_reader
import perimeter
from util import arrayToPixel


def doExport(inputFilePath, outputFilePath, resolution):
    mesh = list(stl_reader.read_stl_verticies(inputFilePath))
    (scale, shift, bounding_box) = slice.calculateScaleAndShift(mesh, resolution)
    mesh = list(slice.scaleAndShiftMesh(mesh, scale, shift))
    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)
    for height in range(bounding_box[2]):
        img = Image.new('RGB', (bounding_box[0], bounding_box[1]), "white")  # create a new black image
        pixels = img.load()
        lines = slice.toIntersectingLines(mesh, height)
        prepixel = np.zeros((bounding_box[0], bounding_box[1]), dtype=bool)
        perimeter.linesToVoxels(lines, prepixel)
        arrayToPixel(prepixel, pixels)
        path = outputFilePattern + "-" + str(height) + outputFileExtension
        print("%d/%d: Saving %s"%(height,bounding_box[2],path))
        img.save(path)


def file_choices(choices,fname):
    filename, ext = os.path.splitext(fname)
    if ext == "" or ext not in choices:
        if len(choices) == 1:
            parser.error("file doesn't end with {}".format(choices))
        else:
            parser.error("file doesn't end with one of {}".format(choices))
    return fname

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert STL files to images/gifs')
    parser.add_argument('input', nargs='?', type=lambda s:file_choices((".stl"),s))
    parser.add_argument('output', nargs='?', type=lambda s:file_choices((".png"),s))
    args = parser.parse_args()
    doExport(args.input, args.output, 256)