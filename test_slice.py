import slice
import stl_reader
import unittest
from matplotlib import pyplot
import pylab
from mpl_toolkits.mplot3d import Axes3D
import random
import numpy as np
from util import printBigArray


class TestSlice(unittest.TestCase):
    def testIsAboveAndBelow(self):
        tri = (
            (1, 2, 5),
            (2, 3, 4),
            (3, 2, 1)
        )
        pixels = np.zeros((10,10), dtype=bool)
        self.assertTrue(slice.isAboveAndBelow(tri, 4, pixels))
        self.assertFalse(slice.isAboveAndBelow(tri, 5, pixels))
        self.assertTrue(pixels[1][2])
        self.assertFalse(slice.isAboveAndBelow(tri, 1, pixels))
        self.assertTrue(pixels[3][2])
        self.assertFalse(slice.isAboveAndBelow(tri, 5.5, pixels))
        self.assertFalse(slice.isAboveAndBelow(tri, 0, pixels))


    def testIsAboveAndBelow_inclusive(self):
        tri = [
            [1, 2, 5],
            [2, 3, 5],
            [3, 2, 1]
        ]
        self.assertTrue(slice.isAboveAndBelow(tri, 5, []))

    def test_wherelinecrossesz(self):
        p1 = (2, 4, 1)
        p2 = (1, 2, 5)
        self.assertEqual(slice.whereLineCrossesZ(p1, p2, 1), p1)
        self.assertEqual(slice.whereLineCrossesZ(p1, p2, 5), p2)
        self.assertEqual(slice.whereLineCrossesZ(p1, p2, 3), (1.5, 3, 3))
        self.assertEqual(slice.whereLineCrossesZ([0, 0, 0], [0, 1, 1], 0.5), (0.0, 0.5, 0.5))


    def test_linearInterpolation(self):
        p1 = (2, 4, 1)
        p2 = (1, 2, 5)
        self.assertEqual(slice.linearInterpolation(p1, p2, 0), p1)
        self.assertEqual(slice.linearInterpolation(p1, p2, 1), p2)
        self.assertEqual(slice.linearInterpolation(p1, p2, .5), (1.5, 3, 3))


    def test_toVoxels(self):
        # mesh = list(stl_reader.read_stl_verticies("./stls/sphere.stl"))
        # lines = slice.slice(mesh, 1)
        # slice.toVoxels(lines)
        pass

    def test_triangleToIntersectingLines(self):
        tri = [
            [2, 4, 1],
            [1, 2, 5],
            [3, 2, 3]
        ]
        actual = list(slice.triangleToIntersectingLines(tri, 4))
        expected = [
            (1.25, 2.5, 4.0), 
            (2.0, 2.0, 4.0)
        ]
        self.assertEqual(actual, expected)


    def test_triangleToIntersectingLines_onePointSame(self):
        tri = [
            (2, 4, 1),
            (1, 2, 5),
            (3, 2, 3)
        ]
        lines = list(slice.triangleToIntersectingLines(tri, 3))
        self.assertEqual([(1.5, 3, 3), (3, 2, 3)], lines)

    def test_triangleToIntersectingLines_twoPointSame(self):
        tri = [
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ]
        lines = list(slice.triangleToIntersectingLines(tri, 3))
        self.assertEqual([tri[0], tri[1]], sorted(lines))


    # def test_toVoxels(self):
    #     lines = [
    #         [[3, 0, 7], [0, 3, 7]],
    #         [[3, 7, 7], [0, 3, 7]],
    #         [[3, 7, 7], [7, 3, 7]],
    #         [[3, 0, 7], [7, 3, 7]],
    #     ]
    #     expected = [[False, False, False, True, True, False, False, False],
    #                 [False, False, True, True, True, True, False, False],
    #                 [False, True, True, True, True, True, True, False],
    #                 [True, True, True, True, True, True, True, True],
    #                 [True, True, True, True, True, True, True, True],
    #                 [False, True, True, True, True, True, True, False],
    #                 [False, False, True, True, True, True, False, False],
    #                 [False, False, False, True, True, False, False, False]]
    #     printBigArray(slice.toVoxels(lines, 8, 8))
        # self.assertTrue((expected==)
