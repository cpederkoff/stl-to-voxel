from setuptools import setup

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='stl-to-voxel',
    version='0.9.1',
    description='Turn STL files into voxels, images, and videos',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='stl python voxel',
    author='Christian Pederkoff',
    url='https://github.com/cpederkoff/stl-to-voxel',
    download_url='https://github.com/cpederkoff/stl-to-voxel/releases',
    install_requires=['numpy', 'Pillow', 'matplotlib'],
    py_modules=['perimeter', 'slice', 'stl_reader', 'stltovoxel', 'util'],
    python_requires='>=3',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
