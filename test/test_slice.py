import numpy as np
import unittest

from stltovoxel import slice


class TestSlice(unittest.TestCase):
    def test_where_line_crosses_z(self):
        p1 = np.array([2, 4, 1])
        p2 = np.array([1, 2, 5])
        self.assertTrue((slice.where_line_crosses_z(p1, p2, 1) == p1).all())
        self.assertTrue((slice.where_line_crosses_z(p1, p2, 5) == p2).all())
        self.assertTrue((slice.where_line_crosses_z(p1, p2, 3) == np.array([1.5, 3, 3])).all())
        self.assertTrue((slice.where_line_crosses_z(np.array([0, 0, 0]), np.array([0, 1, 1]), 0.5) ==
                         np.array([0.0, 0.5, 0.5])).all())

    def test_linear_interpolation(self):
        p1 = np.array([2, 4, 1])
        p2 = np.array([1, 2, 5])
        self.assertTrue((slice.linear_interpolation(p1, p2, 0) == p1).all())
        self.assertTrue((slice.linear_interpolation(p1, p2, 1) == p2).all())
        self.assertTrue((slice.linear_interpolation(p1, p2, .5) == np.array([1.5, 3, 3])).all())

    def test_triangle_to_intersecting_lines(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 1],
            [1, 2, 5],
            [3, 2, 3]
        ])
        slice.triangle_to_intersecting_lines(tri, 4, pixels, lines)
        expected = np.array([
            ((1.25, 2.5, 4.0), (2.0, 2.0, 4.0)),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangle_to_intersecting_lines_one_point_same(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            (2, 4, 1),
            (1, 2, 5),
            (3, 2, 3)
        ])
        slice.triangle_to_intersecting_lines(tri, 3, pixels, lines)
        expected = np.array([
            ((1.5, 3, 3), (3, 2, 3)),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangle_to_intersecting_lines_two_point_same(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ])
        slice.triangle_to_intersecting_lines(tri, 3, pixels, lines)
        expected = np.array([
            (tri[0], tri[1]),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangle_to_intersecting_lines_three_point_same(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 3],
        ])
        slice.triangle_to_intersecting_lines(tri, 3, pixels, lines)
        expected = np.array([
            (tri[0], tri[1]),
            (tri[0], tri[2]),
            (tri[1], tri[2]),
        ])
        self.assertTrue((expected == lines).all())

    def test_triangle_to_intersecting_lines_intersect_one_point(self):
        pixels = np.zeros((100, 100), dtype=bool)
        lines = []
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ])
        slice.triangle_to_intersecting_lines(tri, 5, pixels, lines)
        expected = []
        self.assertEqual(expected, lines)
