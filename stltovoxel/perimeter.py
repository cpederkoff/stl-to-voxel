from functools import reduce


def lines_to_voxels(line_list, pixels):
    current_line_indices = set()
    x = 0
    for (event_x, status, line_ind) in generate_line_events(line_list):
        while event_x - x >= 0:
            lines = reduce(lambda acc, cur: acc + [line_list[cur]], current_line_indices, [])
            paint_y_axis(lines, pixels, x)
            x += 1

        if status == 'start':
            assert line_ind not in current_line_indices
            current_line_indices.add(line_ind)
        elif status == 'end':
            assert line_ind in current_line_indices
            current_line_indices.remove(line_ind)


def generate_y(p1, p2, x):
    x1, y1 = p1[:2]
    x2, y2 = p2[:2]
    dy = (y2 - y1)
    dx = (x2 - x1)
    y = dy * (x - x1) / dx + y1
    return y


def paint_y_axis(lines, pixels, x):
    is_black = False
    target_ys = list(map(lambda line: int(generate_y(line[0], line[1], x)), lines))
    target_ys.sort()
    if len(target_ys) % 2:
        print('[Warning] The number of lines is odd')
        distances = []
        for i in range(len(target_ys) - 1):
            distances.append(target_ys[i+1] - target_ys[i])
        # https://stackoverflow.com/a/17952763
        min_idx = -min((x, -i) for i, x in enumerate(distances))[1]
        del target_ys[min_idx]

    yi = 0
    for target_y in target_ys:
        if is_black:
            # Bulk assign all pixels between yi -> target_y
            pixels[yi:target_y, x] = True
        pixels[target_y][x] = True
        is_black = not is_black
        yi = target_y
    assert is_black is False, 'an error has occured at x%s' % x


def generate_line_events(line_list):
    events = []
    for i, line in enumerate(line_list):
        first, second = sorted(line, key=lambda pt: pt[0])
        events.append((first[0], 'start', i))
        events.append((second[0], 'end', i))
    return sorted(events, key=lambda tup: tup[0])


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
