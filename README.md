# stl-to-voxel
Turn STL files into voxels, images, and videos
### Main Features
* Convert stl files into a voxel representation
* Output to (a series of) .pngs, .xyz, .svx
* Command line interface

### How to run
```
$ pip install git+https://github.com/cpederkoff/stl-to-voxel.git
$ stltovoxel my_input_file.stl my_output_files.png
```

```
$ pip install git+https://github.com/cpederkoff/stl-to-voxel.git
>>> import stltovoxel
>>> stltovoxel.convert_file('my_input_file.stl', 'my_output_files.png')
```

```
$ git clone https://github.com/cpederkoff/stl-to-voxel.git
$ cd stl-to-voxel
$ python3 -m stltovoxel.main my_input_file.stl my_output_files.png
```

<!--- https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl --->

The resolution is optional and defaults to 100.

### Example: 
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/stanford_bunny.png "STL version of the stanford bunny")
![alt text](https://github.com/rcpedersen/stl-to-voxel/raw/master/data/stanford_bunny.gif "voxel version of the stanford bunny")
