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
        ('atttr', '<i2', (1,) )
    ])
    data = np.fromfile(fp, dtype=record_dtype, count=Numtri)
    fp.close()

    Normals = data['normals']
    Vertex1 = data['Vertex1']
    Vertex2 = data['Vertex2']
    Vertex3 = data['Vertex3']

    p = np.append(Vertex1, Vertex2, axis=0)
    p = np.append(p, Vertex3, axis=0)  #list(v1)
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
                assert words[0] == 'vertex'
                verticies.append((float(words[1]), float(words[2]), float(words[3])))

    return triangles

def IsAsciiStl(fname):
    with open(fname,'rb') as input_data:
        line = input_data.readline()
        if line[:5] == b'solid':
            return True
        else:
            return False


def read_stl_verticies(fname):
    if IsAsciiStl(fname):
        for (i,j,k) in AsciiSTL(fname):
            yield (tuple(i),tuple(j),tuple(k))
    else:
        head, p, n, v1, v2, v3 = BinarySTL(fname)
        for i, j, k in zip(v1, v2, v3):
            yield (tuple(i), tuple(j), tuple(k))


