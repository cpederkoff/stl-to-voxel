import slice
import unittest
import numpy as np


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
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = [
            [2, 4, 1],
            [1, 2, 5],
            [3, 2, 3]
        ]
        slice.triangleToIntersectingLines(tri, 4, pixels, lines)
        expected = [
            ((1.25, 2.5, 4.0), (2.0, 2.0, 4.0)),
        ]
        self.assertEqual(expected, lines)

    def test_triangleToIntersectingLines_onePointSame(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = [
            (2, 4, 1),
            (1, 2, 5),
            (3, 2, 3)
        ]
        slice.triangleToIntersectingLines(tri, 3, pixels, lines)
        expected = [
            ((1.5, 3, 3), (3, 2, 3)),
        ]
        self.assertEqual(expected, lines)

    def test_triangleToIntersectingLines_twoPointSame(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = [
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ]
        slice.triangleToIntersectingLines(tri, 3, pixels, lines)
        expected = [
            (tri[0], tri[1]),
        ]
        self.assertEqual(expected, lines)
