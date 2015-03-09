import random
import perimeter
import numpy as np
import unittest
import slice
from util import printBigArray


class PerimeterTest(unittest.TestCase):
    def test_order(self):
        test = [[(0, 0, 2), (0, 2, 2)], [(0, 2, 2), (0, 3, 2)],
                [(2, 0, 2), (3, 0, 2)], [(0, 0, 2), (2, 0, 2)],
                [(0, 3, 2), (2, 3, 2)], [(2, 3, 2), (3, 3, 2)],
                [(3, 2, 2), (3, 3, 2)], [(3, 0, 2), (3, 2, 2)]]


        perim = perimeter.orderIntoPerimeter(test)
        self.assertIsInstance(perim, list)
        self.assertIsInstance(perim[0], tuple)
        start = perim[0]
        for pt in perim[1:]:
            self.assertTrue(
                [start,pt] in test or
                [pt,start] in test
                , [start,pt])
            start = pt
        self.assertEqual(len(test),len(perim), perim)

    def test_order_multi_perimeters(self):
        test = [[(0, 0, 2), (0, 2, 2)], [(0, 2, 2), (0, 3, 2)],
                [(2, 0, 2), (3, 0, 2)], [(0, 0, 2), (2, 0, 2)],
                [(0, 3, 2), (2, 3, 2)], [(2, 3, 2), (3, 3, 2)],
                [(3, 2, 2), (3, 3, 2)], [(3, 0, 2), (3, 2, 2)]]

        test.extend([[(10, 0, 2), (10, 2, 2)], [(10, 2, 2), (10, 3, 2)],
                     [(12, 0, 2), (13, 0, 2)], [(10, 0, 2), (12, 0, 2)],
                     [(10, 3, 2), (12, 3, 2)], [(12, 3, 2), (13, 3, 2)],
                     [(13, 2, 2), (13, 3, 2)], [(13, 0, 2), (13, 2, 2)]])

        expected = [[[(0, 0, 2), (0, 2, 2)], [(0, 2, 2), (0, 3, 2)],
                     [(2, 0, 2), (3, 0, 2)], [(0, 0, 2), (2, 0, 2)],
                     [(0, 3, 2), (2, 3, 2)], [(2, 3, 2), (3, 3, 2)],
                     [(3, 2, 2), (3, 3, 2)], [(3, 0, 2), (3, 2, 2)]]]

        expected.append([[(10, 0, 2), (10, 2, 2)], [(10, 2, 2), (10, 3, 2)],
                         [(12, 0, 2), (13, 0, 2)], [(10, 0, 2), (12, 0, 2)],
                         [(10, 3, 2), (12, 3, 2)], [(12, 3, 2), (13, 3, 2)],
                         [(13, 2, 2), (13, 3, 2)], [(13, 0, 2), (13, 2, 2)]])
        perims = perimeter.separatePerimeters(test)
        self.assertIsInstance(perims, list)
        self.assertIsInstance(perims[0], list)
        self.assertEqual(len(perims[0]), 8)
        self.assertIsInstance(perims[0][0], list)
        self.assertIsInstance(perims[0][0][0], tuple)
        for perim in perims:

            if perim[0] in expected[0]:
                use = expected[0]
            else:
                use = expected[1]
            self.assertEqual(len(use),len(perim))
            for p1,p2 in perim:
                if [p1,p2] in use:
                    self.assertIn([p1,p2],use)
                    use.remove([p1,p2])
                else:
                    self.assertIn([p2,p1],use)
                    use.remove([p2,p1])


    def test_triangulate(self):
        test = [(0, 0, 2), (0, 2, 2),
                (0, 3, 2), (2, 3, 2),
                (3, 3, 2), (3, 2, 2),
                (3, 0, 2), (2, 0, 2)]
        perimeter.triangulate(test)

    def test_fill_perim(self):
        test = [[(0, 0, 0), (3, 0, 0)],
                [(9, 9, 0), (3, 9, 0)],
                [(3, 0, 0), (9, 9, 0)],
                [(3, 9, 0), (0, 0, 0)]]
        pixels = np.zeros((13, 13), dtype=bool)
        perimeter.fillPerimeter(test,pixels)
        printBigArray(pixels)

    def test_fill_perim_trans(self):
        test = [[(0, 0, 0), (0, 3, 0)],
                [(9, 9, 0), (9, 3, 0)],
                [(0, 3, 0), (9, 9, 0)],
                [(9, 3, 0), (0, 0, 0)]]
        pixels = np.zeros((13, 13), dtype=bool)
        perimeter.fillPerimeter(test,pixels)
        printBigArray(pixels)

    def test_cross_line(self):
        self.assertTrue(perimeter.onLine([(0,0,0),(2,2,0)],1,1))
        self.assertTrue(perimeter.onLine([(2,2,0),(0,0,0)],1,1))
        self.assertFalse(perimeter.onLine([(2,2,0),(0,0,0)],2,1))
        self.assertFalse(perimeter.onLine([(2,2,0),(0,0,0)],1,2))
        self.assertTrue(perimeter.onLine([(0,0,0),(4,2,0)],2,1))

    def test_fill_perimeter(self):
        test = [[(0, 0, 2), (0, 2, 2)], [(0, 2, 2), (0, 3, 2)],
                [(2, 0, 2), (3, 0, 2)], [(0, 0, 2), (2, 0, 2)],
                [(0, 3, 2), (2, 3, 2)], [(2, 3, 2), (3, 3, 2)],
                [(3, 2, 2), (3, 3, 2)], [(3, 0, 2), (3, 2, 2)],
                [(10, 0, 2), (10, 2, 2)], [(10, 2, 2), (10, 3, 2)],
                [(12, 0, 2), (13, 0, 2)], [(10, 0, 2), (12, 0, 2)],
                [(10, 3, 2), (12, 3, 2)], [(12, 3, 2), (13, 3, 2)],
                [(13, 2, 2), (13, 3, 2)], [(13, 0, 2), (13, 2, 2)]]
        perimeter.triangulatePerimeter(test)


    def test_order_regression(self):
        test = [[(183, 145, 12), (186, 127, 12)], [(174, 161, 12), (183, 145, 12)], [(183, 109, 12), (186, 127, 12)],
                [(161, 174, 12), (174, 161, 12)], [(145, 183, 12), (161, 174, 12)], [(127, 186, 12), (145, 183, 12)],
                [(109, 183, 12), (127, 186, 12)], [(93, 174, 12), (109, 183, 12)], [(93, 174, 12), (80, 161, 12)],
                [(174, 93, 12), (183, 109, 12)], [(174, 93, 12), (161, 80, 12)], [(186, 127, 12), (183, 109, 12)],
                [(183, 145, 12), (186, 127, 12)], [(174, 161, 12), (183, 145, 12)], [(161, 174, 12), (174, 161, 12)],
                [(183, 109, 12), (174, 93, 12)], [(145, 183, 12), (161, 174, 12)], [(127, 186, 12), (145, 183, 12)],
                [(109, 183, 12), (127, 186, 12)], [(93, 174, 12), (109, 183, 12)], [(93, 174, 12), (80, 161, 12)],
                [(109, 71, 12), (127, 68, 12)], [(93, 80, 12), (109, 71, 12)], [(80, 93, 12), (93, 80, 12)],
                [(127, 68, 12), (145, 71, 12)], [(71, 109, 12), (80, 93, 12)], [(145, 71, 12), (161, 80, 12)],
                [(68, 127, 12), (71, 109, 12)], [(71, 145, 12), (68, 127, 12)], [(80, 161, 12), (71, 145, 12)],
                [(71, 145, 12), (80, 161, 12)], [(174, 93, 12), (161, 80, 12)], [(161, 80, 12), (145, 71, 12)],
                [(127, 68, 12), (145, 71, 12)], [(109, 71, 12), (127, 68, 12)], [(93, 80, 12), (109, 71, 12)],
                [(80, 93, 12), (93, 80, 12)], [(71, 109, 12), (80, 93, 12)], [(68, 127, 12), (71, 109, 12)],
                [(68, 127, 12), (71, 145, 12)]]
        res = perimeter.orderIntoPerimeter(test)
        self.assertEqual(20, len(res), res)

if __name__ == '__main__':
    unittest.main()
