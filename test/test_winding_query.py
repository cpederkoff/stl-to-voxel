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
        [((0, 65),
            (0, 32),
            (0, 31),
            (21, 6),
            (21, 5),
            (22, 5),
            (55, 0),
            (84, 16),
            (95, 48),
            (84, 79),
            (84, 80),
            (83, 80),
            (55, 97),
            (0, 65))])


if __name__ == '__main__':
    unittest.main()
