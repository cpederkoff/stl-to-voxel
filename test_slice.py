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

    def test_triangleToIntersectingLines_intersectOnePoint(self):
        tri = [
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ]
        lines = slice.triangleToIntersectingLines(tri, 5)
        self.assertEqual(None, lines)
    