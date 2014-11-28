from PIL import Image
import math
import slice
import stl_reader
import numpy as np
import time
import cProfile

def arrayToPixel(array, pixels):
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            if array[i,j]:
                pixels[i,j]= (0,0,0)

def doExport(path, resolution):
    mesh = list(stl_reader.read_stl_verticies(path))
    (scale,shift, bounding_box) = slice.calculateScaleAndShift(mesh, resolution)
    mesh = list(slice.scaleAndShiftMesh(mesh, scale, shift))
    for h in range(bounding_box[2]):
        img = Image.new( 'RGB', (bounding_box[0],bounding_box[1]), "white") # create a new black image
        pixels = img.load() # create the pixel map
        perim = slice.slice(mesh,h)
        prepixels = slice.toVoxels(perim,bounding_box[0],bounding_box[1])
        arrayToPixel(prepixels, pixels)
        img.save("./images/"+str(h) + ".png")

if __name__ == '__main__':
    doExport("./stls/legmount.stl", 256)