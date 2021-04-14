# stl-to-voxel
Turn STL files into voxels, images, and videos
### Main Features
* Convert stl files into a voxel representation
* Output to (a series of) .pngs, .xyz, .svx
* Command line interface

### How to run
```
git clone https://github.com/youngkiu/stl-to-voxel.git
$ cd stl-to-voxel

$ python3 stltovoxel.py Pyramid.stl Pyramid.png
# https://www.thingiverse.com/thing:3611495

```
The resolution is optional and defaults to 100.

### Example: 
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/stanford_bunny.png "STL version of the stanford bunny")
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/stanford_bunny.gif "voxel version of the stanford bunny")
