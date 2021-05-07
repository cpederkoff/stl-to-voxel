from functools import reduce


def linesToVoxels(lineList, pixels):
    current_line_indices = set()
    x = 0
    for (event_x, status, line_ind) in generateEvents(lineList):
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
    if len(lines) % 2:
        print('[Warning] The number of lines is odd')
        eq_coefficients = []
        for line in lines:
            eq_coefficient = slope_intercept(line[0], line[1])
            if eq_coefficient in eq_coefficients:
                lines.remove(line)
                break
            eq_coefficients.append(eq_coefficient)
        else:
            raise Exception('Not found the same line')

    isBlack = False
    targetYs = list(map(lambda line: int(generateY(line[0], line[1], x)), lines))
    targetYs.sort()
    yi = 0
    for targetY in targetYs:
        if isBlack:
            for y in range(yi, targetY):
                pixels[x][y] = True
        pixels[x][targetYs] = True
        isBlack = not isBlack
        yi = targetY
    assert isBlack is False, 'an error has occured at x%s' % x


def generateEvents(lineList):
    events = []
    for i, line in enumerate(lineList):
        first, second = sorted(line, key=lambda pt: pt[0])
        events.append((first[0], 'start', i))
        events.append((second[0], 'end', i))
    return sorted(events, key=lambda tup: tup[0])


def isRelevantLines(line, x, pixels):
    above = list(filter(lambda pt: pt[0] > x, line))
    below = list(filter(lambda pt: pt[0] < x, line))
    same = list(filter(lambda pt: pt[0] == x, line))
    if above and below:
        return True
    elif same and above:
        return True
    elif len(same) == 2:
        start = min(int(same[0][1]), int(same[1][1]))
        stop = max(int(same[0][1]), int(same[1][1])) + 1
        for y in range(start, stop):
            pixels[x][y] = True
    else:
        return False
