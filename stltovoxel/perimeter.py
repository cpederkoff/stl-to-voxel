from . import winding_query


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
    x = 0.5
    i = 0
    events = generate_line_events(line_list)
    while i < len(events):
        event_x, status, line_ind = events[i]
        if event_x > x:
            # If the events are ahead of our current x, paint lines
            lines = [line_list[ind] for ind in current_line_indices]
            paint_y_axis(lines, pixels, x)
            x += 1
        elif event_x <= x and status == 'begin':
            # If the events are behind our current x, process them
            assert line_ind not in current_line_indices
            current_line_indices.add(line_ind)
            i += 1
        elif event_x <= x and status == 'end':
            # Process end statuses so that vertical lines are not given to paint_y_axis
            assert line_ind in current_line_indices
            current_line_indices.remove(line_ind)
            i += 1


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
    # If we enter twice, we will continue to be "inside" until we exit twice.
    inside = 0
    target_ys = [generate_y(line[0], line[1], x) for line in lines]
    target_ys.sort()
    assert len(target_ys) % 2 == 0

    yi = 0
    for target_y, inside_change in target_ys:
        # Round causes the center of the voxel to be considered.
        target_y = round(target_y)
        assert target_y >= 0
        if inside > 0:
            # Bulk assign all pixels between yi -> target_y
            pixels[yi:target_y, int(x)] = True

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
