# stl-to-voxel
Turn STL files into voxels, images, and videos
## Main Features
* Convert stl files into a voxel representation
* Output to (a series of) .pngs, .xyz, .svx
* Command line interface

## How to run
### Run in command line
```
$ pip install git+https://github.com/cpederkoff/stl-to-voxel.git
$ stltovoxel input.stl output.png
```

### Multiple materials
```
$ stltovoxel input1.stl input2.stl output.png --colors "red,green"
```
Hex color values are also supported
```
$ stltovoxel input1.stl input2.stl output.png --colors "#FF0000,#00FF00"
```

### Integrate into your code
```
$ pip install git+https://github.com/cpederkoff/stl-to-voxel.git
>>> import stltovoxel
>>> stltovoxel.convert_file('input.stl', 'output.png')
```

### Run manually for testing
```
$ git clone https://github.com/cpederkoff/stl-to-voxel.git
$ cd stl-to-voxel
$ python3 -m stltovoxel.main input.stl output.png
```

<!--- https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl --->

The resolution is optional and defaults to 100.

### Example: 
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/stanford_bunny.png "STL version of the stanford bunny")
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/stanford_bunny.gif "voxel version of the stanford bunny")
### Multi-color Example:
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/traffic_cone_1.png "STL version of the orange part of the model")
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/traffic_cone_2.png "STL version of the white part of the model")
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/traffic_cone.gif "voxel version of the traffic cone")
Credit to https://www.thingiverse.com/thing:21773/files for the model