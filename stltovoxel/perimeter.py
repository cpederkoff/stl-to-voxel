from . import winding_query
import pdb
import matplotlib.pyplot as plt
import math
import time


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
        x1, y1 = p1[:2]
        x2, y2 = p2[:2]
        dx = x2 - x1
        dy = y2 - y1
        ax.plot([x1, x2], [y1, y2])
        ax.arrow(x1, y1, dx/2, dy/2, head_width=0.1, head_length=0.1, fc='k', ec='k')

def plot_line_segments_pixels(line_segments, pixels):
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
        x1, y1 = p1[:2]
        x2, y2 = p2[:2]
        dx = x2 - x1
        dy = y2 - y1
        ax.plot([x1, x2], [y1, y2])
        ax.arrow(x1, y1, dx/2, dy/2, head_width=0.1, head_length=0.1, fc='k', ec='k')
    for y in range(pixels.shape[0]):
        for x in range(pixels.shape[1]):
            xoff = -.5
            yoff = .5
            plt.gca().add_patch(plt.Rectangle((x + xoff,y + yoff), 1, 1, fill=False))
            if pixels[y][x]:
                plt.plot(x + .5 + xoff, y + .5+ yoff, 'ro')
            else:
                plt.plot(x + .5 + xoff, y + .5+ yoff, 'bo')


    # Show the plot
    plt.show()

def plot_polylines(polylines):
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

        middle_ind = int(len(polyline)/2)

        if len(polyline) <= middle_ind+1:
            middle_ind = 0
        x1, y1 = polyline[middle_ind]
        x2, y2 = polyline[middle_ind+1]
        dx = x2 - x1
        dy = y2 - y1
        ax.arrow(x1, y1, dx/2, dy/2, head_width=0.1, head_length=0.1, fc='k', ec='k')
    
    # Show the plot
    plt.show()


def repaired_lines_to_voxels(line_list, pixels):
    if not line_list:
        return
    wq = winding_query.WindingQuery([[tuple(pt.tolist())[:2] for pt in seg] for seg in line_list])
    wq.repair_all()
    new_line_list = []
    for polyline in wq.loops:
        for i in range(len(polyline) - 1):
            new_line_list.append((polyline[i], polyline[i+1]))
    lines_to_voxels(new_line_list, pixels)

def lines_to_voxels(line_list, pixels):
    current_line_indices = set()
    x = 0
    i = 0
    events = generate_line_events(line_list)
    while i < len(events):
        event_x, status, line_ind = events[i]
        if event_x <= x and status == 'begin':
            # If the events are behind our current x, process them
            assert line_ind not in current_line_indices
            current_line_indices.add(line_ind)
            i += 1
        elif event_x <= x and status == 'end':
            # Process end statuses so that vertical lines are not given to paint_y_axis
            assert line_ind in current_line_indices
            current_line_indices.remove(line_ind)
            i += 1
        elif event_x > x:
            # If the events are ahead of our current x, paint lines
            lines = [line_list[ind] for ind in current_line_indices]
            paint_y_axis(lines, pixels, x)
            x += 1
    plot_line_segments_pixels(line_list, pixels)
    time.sleep(2)

def generate_y(p1, p2, x):
    x1, y1 = p1[:2]
    x2, y2 = p2[:2]
    assert x1 != x2

    dy = (y2 - y1)
    dx = (x2 - x1)
    y = dy * (x - x1) / dx + y1

    inside_change = 0
    if x1 > x2:
        inside_change = -1
    elif x1 < x2:
        inside_change = 1
    return y, inside_change


def paint_y_axis(lines, pixels, x):
    # Counting the number of times we enter the inside of a part helps properly handle parts with multiple shells
    # If we enter the inside of a part twice, we must exit the part twice before we stop adding white pixels.
    inside = 0
    target_ys = [generate_y(line[0], line[1], x) for line in lines]
    target_ys.sort()
    assert len(target_ys) % 2 == 0

    yi = 0
    for target_y, inside_change in target_ys:
        target_y = int(target_y)
        assert target_y >= 0
        if inside > 0:
            # Bulk assign all pixels between yi -> target_y
            pixels[yi:target_y, x] = True

        inside += inside_change
        yi = target_y
    assert inside == 0, 'an error has occured at x%s inside:%s lines:%s' % (x, inside, lines)

def generate_line_events(line_list):
    events = []
    for i, line in enumerate(line_list):
        first, second = sorted(line, key=lambda pt: pt[0])
        if first[0] == second[0]:
            # Ignore vertical lines
            continue
        events.append((first[0], 'begin', i))
        events.append((second[0], 'end', i))
    # Sorting by x value, then put all begin events before end events
    return sorted(events)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # python stltovoxel.py data/Model.stl data/Model.png 1024
    lines = [
        ((478.1953748963024, 685.5971369469289, 390.0), (474.987648897627, 682.7858002239518, 390.0)),
        ((478.6458712360894, 708.867925235024, 390.0), (476.80635493021373, 709.6422457310404, 390.0)),
        ((476.8066506675348, 704.1490977931986, 390.0), (478.9686356730549, 707.4220913093288, 390.0)),
        ((475.51186735002426, 568.0120562125561, 390.0), (477.6508098598742, 568.5847941911843, 390.0)),
        ((476.9319294711261, 643.620807438934, 390.0), (477.55874656005545, 643.8324324309802, 390.0)),
        ((477.6538957136681, 644.1949502652121, 390.0), (476.50764488546764, 647.3730220867313, 390.0)),
        ((477.1678215835232, 574.2494597833005, 390.0), (475.625871469434, 575.2964648366983, 390.0)),
        ((476.71719857029177, 276.879543451238, 390.0), (478.92572111642284, 275.85023482493455, 390.0)),
        ((475.7395840585432, 726.9413018914573, 390.0), (477.6455166631113, 728.1006656939942, 390.0)),
        ((480.1531171455746, 424.8577588241842, 390.0), (474.50256297902456, 421.5806451519458, 390.0)),
        ((476.33245691945507, 647.8338656180929, 390.0), (477.3585664525454, 650.5878998039989, 390.0))
    ]
    x = 477
    target_ys = [684, 709, 704, 568, 643, 646, 574, 276, 727, 423, 649]
    for (p1, p2) in lines:
        x_values = [p1[0], p2[0]]
        y_values = [p1[1], p2[1]]

        plt.plot(x_values, y_values)
    for y in target_ys:
        plt.plot(x, y, 'o')
    plt.show()
