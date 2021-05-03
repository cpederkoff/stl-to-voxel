import perimeter
import numpy as np
import unittest


class PerimeterTest(unittest.TestCase):
    def test_lines_to_pixels(self):
        test = [[(0, 0, 0), (3, 0, 0)],
                [(9, 9, 0), (3, 9, 0)],
                [(3, 0, 0), (9, 9, 0)],
                [(3, 9, 0), (0, 0, 0)]]
        actual = np.zeros((13, 13), dtype=bool)
        perimeter.linesToVoxels(test, actual)
        expected = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.assertEqual(expected, actual.astype(int).tolist())

    def test_cross_line(self):
        self.assertTrue(perimeter.onLine([(0, 0, 0), (2, 2, 0)], 1, 1))
        self.assertTrue(perimeter.onLine([(2, 2, 0), (0, 0, 0)], 1, 1))
        self.assertFalse(perimeter.onLine([(2, 2, 0), (0, 0, 0)], 2, 1))
        self.assertFalse(perimeter.onLine([(2, 2, 0), (0, 0, 0)], 1, 2))
        self.assertTrue(perimeter.onLine([(0, 0, 0), (4, 2, 0)], 2, 1))


if __name__ == '__main__':
    unittest.main()
