import matplotlib.pyplot as plt


def plot_line_segments_pixels(line_segments, pixels):
    # Loop over each line segment and plot it using the plot function
    for p1, p2 in line_segments:
        x1, y1 = p1[:2]
        x2, y2 = p2[:2]
        dx = x2 - x1
        dy = y2 - y1
        plt.plot([x1, x2], [y1, y2])
        plt.arrow(x1, y1, dx/2, dy/2, head_width=0.1, head_length=0.1, fc='k', ec='k')
    for y in range(pixels.shape[0]):
        for x in range(pixels.shape[1]):
            xoff = 0
            yoff = 0
            plt.gca().add_patch(plt.Rectangle((x + xoff, y + yoff), 1, 1, fill=False))
            if pixels[y][x]:
                plt.plot(x + .5 + xoff, y + .5 + yoff, 'ro')
            else:
                plt.plot(x + .5 + xoff, y + .5 + yoff, 'bo')

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
    _, ax = plt.subplots()
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
