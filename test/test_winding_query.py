import unittest
import math

from stltovoxel import winding_query


class TestWindingQuery(unittest.TestCase):

    def test_find_polylines_cycle(self):
        line_segments = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]
        expected_polylines = [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
        actual_polylines = winding_query.find_polylines(line_segments)
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
        actual_polylines = winding_query.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)

    def test_find_polylines_out_of_order(self):
        line_segments = [((0, 0), (1, 0)), ((-1, 0), (0, 0)), ((1, 0), (1, 1))]
        expected_polylines = [[(-1, 0), (0, 0), (1, 0), (1, 1)]]
        actual_polylines = winding_query.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)


if __name__ == '__main__':
    unittest.main()
