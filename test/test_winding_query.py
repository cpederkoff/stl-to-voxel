import numpy as np
import unittest
import math
import matplotlib.pyplot as plt
import pdb


from stltovoxel import winding_query
def plot_line_segments(line_segments):
    """
    Plots a list of line segments using pyplot.
    
    Parameters:
    line_segments (list): A list of tuples, where each tuple represents a line segment.
                          Each tuple should contain four floats representing the x and y
                          coordinates of the start and end points of the line segment.
                          
    Returns:
    None
    """
    # Create a new figure
    fig, ax = plt.subplots()
    
    # Loop over each line segment and plot it using the plot function
    for p1, p2 in line_segments:
        x1, y1 = p1
        x2, y2 = p2
        ax.plot([x1, x2], [y1, y2])
    
    # Show the plot
    plt.show()
def plot_polyline(polylines):
    """
    Plots a polyline using pyplot.
    
    Parameters:
    polyline (list): A list of (x,y) tuples representing the vertices of the polyline.
                          
    Returns:
    None
    """
    # Create a new figure
    fig, ax = plt.subplots()
    for polyline in polylines:
        # Extract the x and y coordinates from the polyline
        x_coords, y_coords = zip(*polyline)
    
        # Plot the polyline using the plot function
        ax.plot(x_coords, y_coords)
    
    # Show the plot
    plt.show()

class TestWindingQuery(unittest.TestCase):
    # def test_winding_query(self):
    #     segments = [
    #         [(10,10), (20,10)],
    #         [(20,10), (30,10)],
    #         [(30,10), (40,10)],
    #         [(40,10), (30,20)],
    #         [(30,20), (40,40)],
    #         [(40,40), (10,40)],
    #         [(10,40), (10,9.9)],
    #     ]
    #     wq = winding_query.WindingQuery(segments)
    #     self.assertAlmostEqual(wq.query_winding((35,35)), math.pi*2, places=2)
    #     self.assertAlmostEqual(wq.query_winding((35,24)), 0, places=2)
    #     self.assertAlmostEqual(wq.query_winding((35,12)), math.pi*2, places=2)

    # def test_find_polylines_cycle(self):
    #     line_segments = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]
    #     expected_polylines = [[(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
    #     actual_polylines = winding_query.find_polylines(line_segments)
    #     self.assertEqual(actual_polylines, expected_polylines)

    # def test_find_polylines_no_cycle(self):
    #     line_segments = [((0, 0), (1, 0)), ((1, 0), (2, 1)), ((3, 1), (4, 0)), ((4, 0), (5, 0)), ((5, 0), (6, 1)), ((7, 1), (8, 0)), ((8, 0), (9, 0))]
    #     expected_polylines = [[(0, 0), (1, 0), (2, 1)], [(3, 1), (4, 0), (5, 0), (6, 1)], [(7, 1), (8, 0), (9, 0)]]
    #     actual_polylines = winding_query.find_polylines(line_segments)
    #     self.assertEqual(actual_polylines, expected_polylines)
    
    # def test_find_polylines_out_of_order(self):
    #     line_segments = [((0, 0), (1, 0)), ((-1, 0), (0, 0)), ((1, 0), (1, 1))]
    #     expected_polylines = [[(-1, 0), (0, 0), (1, 0), (1, 1)]]
    #     actual_polylines = winding_query.find_polylines(line_segments)
    #     self.assertEqual(actual_polylines, expected_polylines)
        
    # def test_regression(self):
    #     segments3 = [
    #         ((55, 0), (84, 16)),
    #         ((84, 16), (95, 48)),
    #         ((95, 48), (84, 79)),
    #         ((84, 79), (84, 80)),
    #         ((84, 80), (83, 80)),
    #         ((83, 80), (55, 97)),
    #         ((0, 65), (0, 32)),
    #         ((0, 32), (0, 31)),
    #         ((0, 31), (21, 6)),
    #         ((21, 6), (21, 5)),
    #         ((22, 5), (55, 0)),
    #     ]
    #     wq = winding_query.WindingQuery(segments3)
    #     wq.repair_all()
    #     self.assertEqual(wq.loops, 
    #     [[(55, 0),
    #        (84, 16),
    #        (95, 48),
    #        (84, 79),
    #        (84, 80),
    #        (83, 80),
    #        (55, 97),
    #        (0, 65),
    #        (0, 32),
    #        (0, 31),
    #        (21, 6),
    #        (21, 5),
    #        (22, 5),
    #        (55, 0)]])
    def test_regression_dropped_lines(self):
        input = [[(36.89977264404297, 6.8387451171875), (36.93765640258789, 6.843987464904785)], [(36.58860397338867, 9.527419090270996), (36.588600158691406, 8.159331321716309)], [(36.588600158691406, 8.159331321716309), (36.58860397338867, 8.033574104309082)], [(36.58860397338867, 7.955914497375488), (36.58860397338867, 6.797529697418213)], [(36.58860397338867, 7.984416961669922), (36.58860397338867, 7.955914497375488)], [(36.58860397338867, 8.033574104309082), (36.58860397338867, 7.984416961669922)], [(37.33530807495117, 0.13306432962417603), (37.33530807495117, 6.9024529457092285)], [(37.28316116333008, 6.8944525718688965), (37.33530807495117, 6.9024529457092285)], [(37.23170852661133, 6.886656761169434), (37.28316116333008, 6.8944525718688965)], [(37.1818962097168, 6.879199028015137), (37.23170852661133, 6.886656761169434)], [(37.13523864746094, 6.8723015785217285), (37.1818962097168, 6.879199028015137)], [(37.09225845336914, 6.866016864776611), (37.13523864746094, 6.8723015785217285)], [(37.0534553527832, 6.860397815704346), (37.09225845336914, 6.866016864776611)], [(36.98821258544922, 6.851082801818848), (37.0534553527832, 6.860397815704346)], [(36.93765640258789, 6.843987464904785), (36.98821258544922, 6.851082801818848)], [(36.851829528808594, 6.832220554351807), (36.89977264404297, 6.8387451171875)], [(36.83085632324219, 6.829459190368652), (36.58860397338867, 6.797529697418213)], [(36.83085632324219, 6.829459190368652), (36.851829528808594, 6.832220554351807)]]
        # plot_line_segments(input)
        wq = winding_query.WindingQuery(input)
        plot_polyline(wq.polylines)
        wq.repair_segment()
        plot_line_segments(wq.original_segments)
        wq.collapse_segments()
        plot_polyline(wq.polylines)
        # wq.repair_segment()
        # plot_line_segments(wq.original_segments)
        # # pdb.set_trace()
        # wq.collapse_segments()
        # plot_polyline(wq.polylines)
        # plot_polyline(wq.loops)

if __name__ == '__main__':
    unittest.main()
