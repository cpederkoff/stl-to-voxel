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
    #Note: vol should be addressed with vol[z][x][y]
    vol = np.zeros((bounding_box[2],bounding_box[0],bounding_box[1]), dtype=bool)
    for height in range(bounding_box[2]):
        print('Processing layer %d/%d'%(height+1,bounding_box[2]))
        lines = slice.toIntersectingLines(mesh, height)
        prepixel = np.zeros((bounding_box[0], bounding_box[1]), dtype=bool)
        perimeter.linesToVoxels(lines, prepixel)
        vol[height] = prepixel
    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)
    if outputFileExtension == '.png':
        exportPngs(vol, bounding_box, outputFilePath)
    elif outputFileExtension == '.xyz':
        exportXyz(vol, bounding_box, outputFilePath)
    elif outputFileExtension == '.svx':
        exportSvx(vol, bounding_box, outputFilePath)

def exportPngs(voxels, bounding_box, outputFilePath):
    outputFilePattern, outputFileExtension = os.path.splitext(outputFilePath)
    for height in range(bounding_box[2]):
        img = Image.new('RGB', (bounding_box[0], bounding_box[1]), 'white')  # create a new black image
        pixels = img.load()
        arrayToPixel(voxels[height], pixels)
        path = outputFilePattern + '-' + str(height) + outputFileExtension
        img.save(path)

def exportXyz(voxels, bounding_box, outputFilePath):
    output = open(outputFilePath, 'w')
    for z in bounding_box[2]:
        for x in bounding_box[0]:
            for y in bounding_box[1]:
                if vol[z][x][y]:
                    output.write('%s %s %s\n'%(x,y,z))
    output.close()

def exportSvx(voxels, bounding_box, outputFilePath):
    pass


def file_choices(choices,fname):
    filename, ext = os.path.splitext(fname)
    if ext == '' or ext not in choices:
        if len(choices) == 1:
            parser.error('%s doesn\'t end with %s'%(fname,choices))
        else:
            parser.error('%s doesn\'t end with one of %s'%(fname,choices))
    return fname

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert STL files to images/gifs')
    parser.add_argument('input', nargs='?', type=lambda s:file_choices(('.stl'),s))
    parser.add_argument('output', nargs='?', type=lambda s:file_choices(('.png', '.xyz', '.svx'),s))
    args = parser.parse_args()
    doExport(args.input, args.output, 256)