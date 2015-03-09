from PIL import Image
import numpy as np

import slice
import stl_reader
import perimeter
from util import arrayToPixel


def doExport(path, resolution):
    mesh = list(stl_reader.read_stl_verticies(path))
    (scale, shift, bounding_box) = slice.calculateScaleAndShift(mesh, resolution)
    mesh = list(slice.scaleAndShiftMesh(mesh, scale, shift))
    for height in range(bounding_box[2]):
        img = Image.new('RGB', (bounding_box[0], bounding_box[1]), "white")  # create a new black image
        pixels = img.load()
        lines = slice.toIntersectingLines(mesh, height)
        prepixel = np.zeros((bounding_box[0], bounding_box[1]), dtype=bool)
        perimeter.linesToVoxels(lines, prepixel)
        arrayToPixel(prepixel, pixels)
        img.save("./images/" + str(height) + ".png")


if __name__ == '__main__':
    doExport("/home/christian/PycharmProjects/STLToVoxel/stls/airtripper-extruder-v3-all.stl", 256)
    # cProfile.run('doExport("/home/christian/PycharmProjects/STLToVoxel/stls/airtripper-extruder-v3-all.stl", 256)')