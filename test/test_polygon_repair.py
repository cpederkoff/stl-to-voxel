import numpy as np
import unittest

from stltovoxel import polygon_repair


class TestPolygonRepair(unittest.TestCase):
    def tuples_almost_equal(self, actual, expected):
        for ac_val, exp_val in zip(actual, expected):
            self.assertAlmostEqual(ac_val, exp_val, 3, f"{actual} != {expected}")

    def test_find_polylines_cycle(self):
        line_segments = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]
        expected_polylines = [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
        actual_polylines = polygon_repair.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)

    def test_find_polylines_no_cycle(self):
        line_segments = [
            ((0, 0), (1, 0)),
            ((1, 0), (2, 1)),
            ((3, 1), (4, 0)),
            ((4, 0), (5, 0)),
            ((5, 0), (6, 1)),
            ((7, 1), (8, 0)),
            ((8, 0), (9, 0))
        ]
        expected_polylines = [[(0, 0), (1, 0), (2, 1)], [(3, 1), (4, 0), (5, 0), (6, 1)], [(7, 1), (8, 0), (9, 0)]]
        actual_polylines = polygon_repair.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)

    def test_find_polylines_out_of_order(self):
        line_segments = [((0, 0), (1, 0)), ((-1, 0), (0, 0)), ((1, 0), (1, 1))]
        expected_polylines = [[(-1, 0), (0, 0), (1, 0), (1, 1)]]
        actual_polylines = polygon_repair.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)

    def test_initial_direction(self):
        segs = [((0, 1), (0, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ]
        pt = (0, 0)
        actual = polygon_repair.initial_direction(pt, segs)
        actual = tuple(actual)
        expected = (1.0, 0)
        self.tuples_almost_equal(actual, expected)

    def test_initial_direction2(self):
        segs = [((0, 1), (1, 1)), ((1, 0), (0, 0))]
        pt = (1, 1)
        actual = polygon_repair.initial_direction(pt, segs)
        actual = tuple(actual)
        expected = polygon_repair.normalize((-1, -1))
        self.tuples_almost_equal(actual, expected)

    def test_initial_direction3(self):
        segs = [((1, 0), (0, 0)), ((1, 1), (1, 0))]
        pt = (0, 0)
        actual = polygon_repair.initial_direction(pt, segs)
        actual = tuple(actual)
        expected = polygon_repair.normalize((1, 1))
        self.tuples_almost_equal(actual, expected)

    def test_winding_contour(self):
        segs = [((0, 0), (1, 0)), ((1, 0), (1, 1))]
        pos = np.array((1, 1)) - np.array((0.1, 0.1))
        # Treats starts as repellers and ends as attractors
        actual = polygon_repair.winding_contour(pos, segs)
        expected = polygon_repair.normalize((-1, -1))
        self.tuples_almost_equal(actual, expected)

    def test_winding_contour2(self):
        segs = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1))]
        pos = (0, 0.5)
        actual = polygon_repair.winding_contour(pos, segs)
        expected = polygon_repair.normalize((0, -1))
        self.tuples_almost_equal(actual, expected)

        pos = (-.5, 0.5)
        actual = polygon_repair.winding_contour(pos, segs)
        expected = polygon_repair.normalize((0, -1))
        self.tuples_almost_equal(actual, expected)

        pos = (.5, 0.5)
        actual = polygon_repair.winding_contour(pos, segs)
        expected = polygon_repair.normalize((0, -1))
        self.tuples_almost_equal(actual, expected)

    def test_winding_contour3(self):
        segs = [((0, 0), (1, 0)), ((1, 1), (0, 1))]
        pos = (0.00001, 0.00001)
        actual = polygon_repair.winding_contour(pos, segs)
        expected = polygon_repair.normalize((-1, -1))
        self.tuples_almost_equal(actual, expected)

    def test_repair_all_close_case(self):
        segs = [((0, 0), (1, 0)), ((1, .5), (0, .5))]
        repair = polygon_repair.PolygonRepair(segs, (10, 10))
        repair.repair_all()
        expected = [[(0, 0), (1, 0), (1, 0.5), (0, 0.5), (0, 0)]]
        self.assertEqual(repair.loops, expected)

    def test_repair_all_far_case(self):
        segs = [((0, 0), (1, 0)), ((1, 1.5), (0, 1.5))]
        repair = polygon_repair.PolygonRepair(segs, (10, 10))
        repair.repair_all()
        expected = [[(0, 0), (1, 0), (0, 0)], [(1, 1.5), (0, 1.5), (1, 1.5)]]
        self.assertEqual(repair.loops, expected)


if __name__ == '__main__':
    unittest.main()
