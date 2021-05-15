import slice
import unittest
import numpy as np


class TestSlice(unittest.TestCase):
    def test_wherelinecrossesz(self):
        p1 = np.array([2, 4, 1])
        p2 = np.array([1, 2, 5])
        self.assertTrue((slice.whereLineCrossesZ(p1, p2, 1) == p1).all())
        self.assertTrue((slice.whereLineCrossesZ(p1, p2, 5) == p2).all())
        self.assertTrue((slice.whereLineCrossesZ(p1, p2, 3) == np.array([1.5, 3, 3])).all())
        self.assertTrue((slice.whereLineCrossesZ(np.array([0, 0, 0]), np.array([0, 1, 1]), 0.5) ==
                         np.array([0.0, 0.5, 0.5])).all())

    def test_linearInterpolation(self):
        p1 = np.array([2, 4, 1])
        p2 = np.array([1, 2, 5])
        self.assertTrue((slice.linearInterpolation(p1, p2, 0) == p1).all())
        self.assertTrue((slice.linearInterpolation(p1, p2, 1) == p2).all())
        self.assertTrue((slice.linearInterpolation(p1, p2, .5) == np.array([1.5, 3, 3])).all())

    def test_triangleToIntersectingLines(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 1],
            [1, 2, 5],
            [3, 2, 3]
        ])
        slice.triangleToIntersectingLines(tri, 4, pixels, lines)
        expected = np.array([
            ((1.25, 2.5, 4.0), (2.0, 2.0, 4.0)),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangleToIntersectingLines_onePointSame(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            (2, 4, 1),
            (1, 2, 5),
            (3, 2, 3)
        ])
        slice.triangleToIntersectingLines(tri, 3, pixels, lines)
        expected = np.array([
            ((1.5, 3, 3), (3, 2, 3)),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangleToIntersectingLines_twoPointSame(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ])
        slice.triangleToIntersectingLines(tri, 3, pixels, lines)
        expected = np.array([
            (tri[0], tri[1]),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangleToIntersectingLines_intersectOnePoint(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ])
        slice.triangleToIntersectingLines(tri, 5, pixels, lines)
        expected = []
        self.assertEqual(expected, lines)
