from functools import reduce


def linesToVoxels(lineList, pixels):
    current_line_indices = set()
    x = 0
    for (event_x, status, line_ind) in generateLineEvents(lineList):
        while event_x - x >= 0:
            lines = reduce(lambda acc, cur: acc + [lineList[cur]], current_line_indices, [])
            paintYaxis(lines, pixels, x)
            x += 1

        if status == 'start':
            assert line_ind not in current_line_indices
            current_line_indices.add(line_ind)
        elif status == 'end':
            assert line_ind in current_line_indices
            current_line_indices.remove(line_ind)


def slope_intercept(p1, p2):
    x1, y1 = p1[:2]
    x2, y2 = p2[:2]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    return slope, intercept


def generateY(p1, p2, x):
    slope, intercept = slope_intercept(p1, p2)
    y = slope * x + intercept
    return y


def paintYaxis(lines, pixels, x):
    isBlack = False
    targetYs = list(map(lambda line: int(generateY(line[0], line[1], x)), lines))
    targetYs.sort()
    if len(targetYs) % 2:
        print('[Warning] The number of lines is odd')
        distances = []
        for i in range(len(targetYs) - 1):
            distances.append(targetYs[i+1] - targetYs[i])
        # https://stackoverflow.com/a/17952763
        min_idx = -min((x, -i) for i, x in enumerate(distances))[1]
        del targetYs[min_idx]

    yi = 0
    for targetY in targetYs:
        if isBlack:
            # Bulk assign all pixels between yi -> targetY
            pixels[yi:targetY, x] = True
        pixels[targetY][x] = True
        isBlack = not isBlack
        yi = targetY
    assert isBlack is False, 'an error has occured at x%s' % x


def generateLineEvents(lineList):
    events = []
    for i, line in enumerate(lineList):
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
    targetYs = [684, 709, 704, 568, 643, 646, 574, 276, 727, 423, 649]
    for (p1, p2) in lines:
        x_values = [p1[0], p2[0]]
        y_values = [p1[1], p2[1]]

        plt.plot(x_values, y_values)
    for y in targetYs:
        plt.plot(x, y, 'o')
    plt.show()
