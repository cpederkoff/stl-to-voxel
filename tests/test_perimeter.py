import unittest

import numpy as np

from stltovoxel.perimeter import lines_to_voxels


class TestPerimeter(unittest.TestCase):
    # Expected output for the test polygon
    EXPECTED_POLYGON = [
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    def test_lines_to_voxels(self):
        test = [
            [(0, 0, 0), (3, 0, 0)],
            [(3, 0, 0), (9, 9, 0)],
            [(9, 9, 0), (3, 9, 0)],
            [(3, 9, 0), (0, 0, 0)],
        ]
        actual = np.zeros((13, 13), dtype=bool)
        lines_to_voxels(test, actual)
        self.assertEqual(self.EXPECTED_POLYGON, actual.astype(int).tolist())

    def test_lines_to_voxels_inverted(self):
        test = [
            [(3, 0, 0), (0, 0, 0)],
            [(9, 9, 0), (3, 0, 0)],
            [(3, 9, 0), (9, 9, 0)],
            [(0, 0, 0), (3, 9, 0)],
        ]
        actual = np.zeros((13, 13), dtype=bool)
        lines_to_voxels(test, actual)
        self.assertEqual(self.EXPECTED_POLYGON, actual.astype(int).tolist())


if __name__ == "__main__":
    unittest.main()
