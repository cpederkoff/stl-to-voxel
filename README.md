# stl-to-voxel
Turn STL files into voxels, images, and videos
## Main Features
* Convert stl files into a voxel representation
* Output to (a series of) .pngs, .xyz, .svx
* Command line interface

## How to run
### Run in command line
```
pip install stl-to-voxel
stltovoxel input.stl output.png
```

### Generating a higher resolution
```bash
stltovoxel input.stl output.png --resolution 200
```

### Specifying voxel size
```bash
stltovoxel input.stl output.png --voxel-size .5
```

### Multiple materials
```bash
stltovoxel input1.stl input2.stl output.png --colors "red,green"
```
Hex color values are also supported
```bash
stltovoxel input1.stl input2.stl output.png --colors "#FF0000,#00FF00"
```

### Integrate into your code
```python3
import stltovoxel
stltovoxel.convert_file('input.stl', 'output.png')
```

### Run for development
```bash
cd stl-to-voxel
python3 -m stltovoxel input.stl output.png
```

### See help
```bash
$ stltovoxel
usage: stltovoxel [-h] [--pad PAD] [--no-parallel] [--colors COLORS] [--resolution RESOLUTION | 
   --resolution-xyz RESOLUTION RESOLUTION RESOLUTION | 
   --voxel-size VOXEL_SIZE | --voxel-size-xyz VOXEL_SIZE VOXEL_SIZE VOXEL_SIZE] input [input ...] output
```

### Run unit tests
```bash
cd stl-to-voxel
PYTHONPATH=./ python3 test/test_slice.py
```

<!--- https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl --->

The resolution is optional and defaults to 100.

### Example:
![alt text](https://github.com/cpederkoff/stl-to-voxel/raw/master/data/stanford_bunny.png "STL version of the stanford bunny")
![alt text](https://github.com/cpederkoff/stl-to-voxel/raw/master/data/stanford_bunny.gif "voxel version of the stanford bunny")
### Multi-color Example:
<p float="left">
  <img src="https://github.com/cpederkoff/stl-to-voxel/raw/master/data/traffic_cone_1.png" width="300" alt="STL version of the orange part of the model">
  <img src="https://github.com/cpederkoff/stl-to-voxel/raw/master/data/traffic_cone_2.png" width="300" alt="STL version of the white part of the model">
  <img src="https://github.com/cpederkoff/stl-to-voxel/raw/master/data/traffic_cone.gif" width="300" alt="voxel version of the traffic cone">
</p>

[Model credit](https://www.thingiverse.com/thing:21773)
