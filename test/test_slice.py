import numpy as np
import unittest

from stltovoxel import slice


class TestSlice(unittest.TestCase):
    def test_calculate_scale_and_shift(self):
        scale, shift, res = slice.calculate_scale_and_shift(np.array([0, 0, 0]), np.array([21, 21, 20]), 10, None)
        self.assertEqual([0.5, 0.5, 0.5], scale)
        self.assertEqual([-0.5, -0.5, 0], shift)
        self.assertEqual([11, 11, 10], res)

        scale, shift, res = slice.calculate_scale_and_shift(np.array([0, 0, 0]), np.array([20.5, 20.5, 20]), 20, None)
        np.testing.assert_array_equal([1, 1, 1], scale)
        np.testing.assert_array_equal([-0.25 ,-0.25 , 0 ], shift)
        np.testing.assert_array_equal([21, 21, 20], res)

        scale, shift, res = slice.calculate_scale_and_shift(np.array([0, 0, 0]), np.array([20.125, 20.125, 20]), 10, None)
        np.testing.assert_array_equal([0.5, 0.5, 0.5], scale)
        np.testing.assert_array_equal([-0.9375, -0.9375, 0.0], shift)
        np.testing.assert_array_equal([11, 11, 10], res)

    def test_where_line_crosses_z(self):
        p1 = np.array([2, 4, 1])
        p2 = np.array([1, 2, 5])
        np.testing.assert_array_equal(slice.where_line_crosses_z(p1, p2, 1), p1)
        np.testing.assert_array_equal(slice.where_line_crosses_z(p1, p2, 5), p2)
        np.testing.assert_array_equal(slice.where_line_crosses_z(p1, p2, 3), np.array([1.5, 3, 3]))
        np.testing.assert_array_equal(
            slice.where_line_crosses_z(np.array([0, 0, 0]), np.array([0, 1, 1]), 0.5),
            np.array([0.0, 0.5, 0.5])
        )

    def test_linear_interpolation(self):
        p1 = np.array([2, 4, 1])
        p2 = np.array([1, 2, 5])
        np.testing.assert_array_equal(slice.linear_interpolation(p1, p2, 0), p1)
        np.testing.assert_array_equal(slice.linear_interpolation(p1, p2, 1), p2)
        np.testing.assert_array_equal(slice.linear_interpolation(p1, p2, .5), np.array([1.5, 3, 3]))

    def test_triangle_to_intersecting_lines(self):
        tri = np.array([
            [2, 4, 1],
            [1, 2, 5],
            [3, 2, 3]
        ])
        expected = np.array([
            [2.0, 2.0, 4.0], 
            [1.25, 2.5, 4.0],
        ])
        np.testing.assert_array_equal(
            slice.triangle_to_intersecting_points(tri, 4), 
            expected
        )
    def test_triangle_to_intersecting_lines_one_point_same(self):
        tri = np.array([
            [2, 4, 1],
            [1, 2, 5],
            [3, 2, 3]
        ])
        expected = np.array([
            tri[2],
            [1.5, 3, 3]
        ])
        np.testing.assert_array_equal(slice.triangle_to_intersecting_points(tri, 3), expected)


    def test_triangle_to_intersecting_lines_two_point_same(self):
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ])
        expected = np.array([
            tri[0], 
            tri[1],
        ])
        np.testing.assert_array_equal(slice.triangle_to_intersecting_points(tri, 3), expected)

    def test_triangle_to_intersecting_lines_three_point_same(self):
        tri = np.array([
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 3],
        ])
        expected = np.array([
            tri[1], 
            tri[2], 
            tri[0], 
        ])
        np.testing.assert_array_equal(slice.triangle_to_intersecting_points(tri, 3), expected)

    def test_triangle_to_intersecting_lines_intersect_one_point(self):
        tri = [
            [2, 4, 3],
            [3, 2, 3],
            [1, 2, 5],
        ]
        expected = np.array([[
            1,2,5
        ]])
        np.testing.assert_array_equal(slice.triangle_to_intersecting_points(tri, 5), expected)



if __name__ == '__main__':
    unittest.main()
