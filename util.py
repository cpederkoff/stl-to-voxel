def manhattan_distance(p1, p2, d=2):
    assert (len(p1) == len(p2))
    all_distances = 0
    for i in range(d):
        all_distances += abs(p1[i] - p2[i])
    return all_distances


def print_big_array(big, yes='1', no='0'):
    print()
    for line in big:
        for char in line:
            if char:
                print(yes, end=" ")
            else:
                print(no, end=" ")
        print()
