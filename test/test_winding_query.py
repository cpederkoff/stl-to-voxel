import numpy as np
import unittest
import math

from stltovoxel import winding_query


class TestWindingQuery(unittest.TestCase):
    def test_winding_query(self):
        segments = [
            [(10,10), (20,10)],
            [(20,10), (30,10)],
            [(30,10), (40,10)],
            [(40,10), (30,20)],
            [(30,20), (40,40)],
            [(40,40), (10,40)],
            [(10,40), (10,9.9)],
        ]
        wq = winding_query.WindingQuery(segments)
        self.assertAlmostEqual(wq.query_winding((35,35)), math.pi*2, places=2)
        self.assertAlmostEqual(wq.query_winding((35,24)), 0, places=2)
        self.assertAlmostEqual(wq.query_winding((35,12)), math.pi*2, places=2)

    def test_find_polylines_cycle(self):
        line_segments = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]
        expected_polylines = [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
        actual_polylines = winding_query.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)

    def test_find_polylines_no_cycle(self):
        line_segments = [((0, 0), (1, 0)), ((1, 0), (2, 1)), ((3, 1), (4, 0)), ((4, 0), (5, 0)), ((5, 0), (6, 1)), ((7, 1), (8, 0)), ((8, 0), (9, 0))]
        expected_polylines = [[(0, 0), (1, 0), (2, 1)], [(3, 1), (4, 0), (5, 0), (6, 1)], [(7, 1), (8, 0), (9, 0)]]
        actual_polylines = winding_query.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)
    
    def test_find_polylines_out_of_order(self):
        line_segments = [((0, 0), (1, 0)), ((-1, 0), (0, 0)), ((1, 0), (1, 1))]
        expected_polylines = [[(-1, 0), (0, 0), (1, 0), (1, 1)]]
        actual_polylines = winding_query.find_polylines(line_segments)
        self.assertEqual(actual_polylines, expected_polylines)
        
    def test_regression(self):
        segments3 = [
            ((55, 0), (84, 16)),
            ((84, 16), (95, 48)),
            ((95, 48), (84, 79)),
            ((84, 79), (84, 80)),
            ((84, 80), (83, 80)),
            ((83, 80), (55, 97)),
            ((0, 65), (0, 32)),
            ((0, 32), (0, 31)),
            ((0, 31), (21, 6)),
            ((21, 6), (21, 5)),
            ((22, 5), (55, 0)),
        ]
        wq = winding_query.WindingQuery(segments3)
        wq.repair_all()
        self.assertEqual(wq.loops, 
        [[(55, 0),
           (84, 16),
           (95, 48),
           (84, 79),
           (84, 80),
           (83, 80),
           (55, 97),
           (0, 65),
           (0, 32),
           (0, 31),
           (21, 6),
           (21, 5),
           (22, 5),
           (55, 0)]])


if __name__ == '__main__':
    unittest.main()
