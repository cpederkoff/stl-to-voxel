from functools import reduce


def linesToVoxels(lineList, pixels):
    current_line_indices = set()
    x = 0
    for (event_x, status, line_ind) in generateEvents(lineList):
        while event_x - x >= 0:
            lines = reduce(lambda acc, cur: acc + [lineList[cur]], current_line_indices, [])
            paintPixels(lines, pixels, x)
            x += 1

        if status == 'start':
            assert line_ind not in current_line_indices
            current_line_indices.add(line_ind)
        elif status == 'end':
            assert line_ind in current_line_indices
            current_line_indices.remove(line_ind)


def paintPixels(lines, pixels, x):
    if len(lines) % 2:
        print('[Warning] The number of lines is odd')

    isBlack = False
    targetYs = list(map(lambda line: int(generateY(line, x)), lines))
    for y in range(len(pixels[x])):
        if isBlack:
            pixels[x][y] = True
        if y in targetYs:
            for line in lines:
                if onLine(line, x, y):
                    isBlack = not isBlack
                    pixels[x][y] = True
    if isBlack:
        raise Exception('an error has occured at x%s' % x)


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


def generateY(line, x):
    ratio = (x - line[0][0]) / (line[1][0] - line[0][0])
    ydist = line[1][1] - line[0][1]
    newy = line[0][1] + ratio * ydist
    return newy


def onLine(line, x, y):
    newy = generateY(line, x)
    if int(newy) != y:
        return False
    if (int(line[0][0]) != x and
        int(line[1][0]) != x) and \
            (max(line[0][0], line[1][0]) < x or
             min(line[0][0], line[1][0]) > x):
        return False
    if (int(line[0][1]) != y and
        int(line[1][1]) != y) and \
            (max(line[0][1], line[1][1]) < y or
             min(line[0][1], line[1][1]) > y):
        return False
    return True


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    lines = [
        ((55.183775000510195, 42.91771076583979, 133.0), (54.664478438939994, 42.91190079807315, 133.0)),
        ((55.05365382117602, 48.399582783540694, 133.0), (54.28259953472679, 48.399582783540694, 133.0)),
        ((54.72938801464095, 51.1054056827822, 133.0), (55.21085292933077, 51.10540695761318, 133.0)),
        ((55.17312327125145, 54.131620716008165, 133.0), (54.72938801464095, 54.13161531213461, 133.0)),
        ((54.28259953472679, 48.399582783540694, 133.0), (55.05365382117602, 48.399582783540694, 133.0)),
        ((55.05365382117602, 50.600419560857354, 133.0), (54.28259953472679, 50.600419560857354, 133.0)),
        ((54.72938801464095, 44.868384133402195, 133.0), (55.21085292933077, 44.868386286857266, 133.0)),
        ((55.183775000510195, 56.0822892341602, 133.0), (54.664478438939994, 56.088101893431286, 133.0)),
        ((55.17312327125145, 47.89459328407937, 133.0), (54.72938801464095, 47.894596812904574, 133.0))
    ]
    x = 55
    targetYs = [42, 48, 51, 54, 48, 50, 44, 56, 47]
    for (p1, p2) in lines:
        x_values = [p1[0], p2[0]]
        y_values = [p1[1], p2[1]]

        plt.plot(x_values, y_values)
    for y in targetYs:
        plt.plot(x, y, 'o')
    plt.show()
