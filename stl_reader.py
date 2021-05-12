# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 06:37:35 2013

@author: Sukhbinder Singh

Reads a Binary file and
Returns Header,Points,Normals,Vertex1,Vertex2,Vertex3

Source: http://sukhbinder.wordpress.com/2013/11/28/binary-stl-file-reader-in-python-powered-by-numpy/

"""
import numpy as np
from struct import unpack


def BinarySTL(fname):
    fp = open(fname, 'rb')
    Header = fp.read(80)
    nn = fp.read(4)
    Numtri = unpack('i', nn)[0]
    record_dtype = np.dtype([
        ('normals', np.float32, (3,)),
        ('Vertex1', np.float32, (3,)),
        ('Vertex2', np.float32, (3,)),
        ('Vertex3', np.float32, (3,)),
        ('atttr', '<i2', (1,))
    ])
    data = np.fromfile(fp, dtype=record_dtype, count=Numtri)
    fp.close()

    Normals = data['normals']
    Vertex1 = data['Vertex1']
    Vertex2 = data['Vertex2']
    Vertex3 = data['Vertex3']

    p = np.append(Vertex1, Vertex2, axis=0)
    p = np.append(p, Vertex3, axis=0)
    Points = np.array(list(set(tuple(p1) for p1 in p)))

    return Header, Points, Normals, Vertex1, Vertex2, Vertex3


def AsciiSTL(fname):
    with open(fname, 'r') as input_data:
        # Skips text before the beginning of the interesting block:
        init = False
        triangles = []
        verticies = []
        for line in input_data:
            if line.strip() == 'outer loop':  # Or whatever test is needed
                init = True
                verticies = []
                continue
            # Reads text until the end of the block:
            elif line.strip() == 'endloop':
                init = False
                triangles.append(verticies)
                continue
            elif init:
                words = line.strip().split(' ')
                words = list(filter(None, words))
                assert words[0] == 'vertex'
                verticies.append((float(words[1]), float(words[2]), float(words[3])))

    return triangles


def IsAsciiStl(fname):
    with open(fname, 'rb') as input_data:
        line = input_data.readline()
        if line[:6] != b'solid ':
            return False
        line = input_data.readline().strip()
        if line[:5] == b'facet':
            return True
        if line[:8] == b'endsolid':
            return True
    return False


def read_stl_verticies(fname):
    if IsAsciiStl(fname):
        triangles = AsciiSTL(fname)
        mesh = np.array(triangles)
    else:
        head, p, n, v1, v2, v3 = BinarySTL(fname)
        mesh = np.hstack((v1[:, np.newaxis], v2[:, np.newaxis], v3[:, np.newaxis]))
    # shape = (n, 3, 3)
    return mesh
