import matplotlib.pyplot as plt
import numpy as np
import math
import pdb

def normalize(num):
    return ((num + math.pi) % (2*math.pi)) - math.pi

def atansum(f1, f2):
    y, x = f1
    z, w = f2
    return (y*w + x*z, x*w - y*z)

def atandiff(f1, f2):
    y1, x1 = f1
    y2, x2 = f2
    return (y1*x2 - x1*y2, x1*x2 + y1*y2)

def negatan(f1):
    y,x = f1
    return -y, x

# calculate baseline from angle of last two line segments of all incomplete loops
## Find a more pleasing way to represent baseline. Angles are good, but the asymmetry is uncomfortable.
# Look at neighbors distance and angle, incorporate baseline, decide who to connect to.
# 
def is_right(line, point):
    a, b = line
    x1, y1 = a
    x2, y2 = b
    x0, y0 = point
    num = ((x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1))
    return num > 0

def corners(segs, pt, step_towards):
    x, y = pt
    # Without a small movement toward the other point the value is undefined
    # because we are at the center of a sweep
    dx, dy = step_towards
    x += dx/1000
    y += dy/1000
    ret = 0
    for i in range(len(segs) - 1):
        s1 = segs[i]
        s2 = segs[i+1]
        assert s1[1] == s2[0]
        a = np.array(list(s1[0]))
        b = np.array(list(s1[1]))
        c = np.array(list(s2[1]))
        l1 = a - b
        l2 = b - c
        
        ang = math.atan2(*atandiff((l2[1], l2[0]), (l1[1], l1[0])))
        
        if ang < 0 : 
            # Concave case 
            if not is_right((a, b), (x,y)) and not is_right((c, b), (x,y)):
                ret += ang + 2 * math.pi
            else: 
                ret += ang 
        else :
            # Convex case (normal)
            if is_right((a, b), (x,y)) and is_right((c, b), (x,y)):
                ret += ang - 2 * math.pi
            else: 
                ret += ang 
    return ret


def edge_start(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    start = s1
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (start[1] - them_pt[1], start[0] - them_pt[0])
    return math.atan2(*atansum(negatan(p1), angle))

def edge_end(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    start = s2
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (start[1] - them_pt[1], start[0] - them_pt[0])
    return math.atan2(*atansum(p1, negatan(angle)))

def edge_end_baseline(me_seg):
    s1, s2 = me_seg
    start = s2
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    return math.atan2(*angle)

def line(segs, inc):
    im = np.zeros((100,100))
    for x in range(-50, 50):
        for y in range(-50, 50):
            answers = []
            for p1, p2 in segs:
                x1, y1 = p1
                x2, y2 = p2
                angle = (y2 - y1, x2 - x1)
                p1 = (y-y1, x-x1)
                p2 = (y-y2, x-x2)
                answers.append(atansum(negatan(p1), angle))
                answers.append(atansum(p2, negatan(angle)))
            accum = 0
            for i in inc:
                accum += math.atan2(*answers[i])

            im[y+50][x+50] = accum
    return im


def get_direction(pos, segs, dangling_end):
    x, y = pos
    accum = 0
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)
    # accum += edge_start(dangling_end, pos)

    base = edge_end_baseline(dangling_end)
    return base - accum

def get_direction_iter(pos, segs, dangling_end, target):
    x, y = pos
    accum = 0
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)
    
    # accum += edge_start(dangling_end, pos)

    base = edge_end_baseline(dangling_end)
    # target - accum is a compensation factor to point back toward the ideal winding number
    print(accum)
    return (base - accum) #+ (target - accum)


def angle_to_delta(theta):
    delta_x = math.cos(theta)
    delta_y = math.sin(theta)
    return np.array([delta_x, delta_y])

segs = [
    ((0,0),(5,-5)),
    ((10,10),(-10,10)),
    ((5,-5), (10,0)),
    ((-10,8), (-10,2)),
    ((-5, 4), (-10, -4)),
]

def find_polyline_endpoints(segs):
    start_to_end = dict()
    end_to_start = dict()

    for start, end in segs:
        # Update connections for the new segment
        actual_start = end_to_start.get(start, start)
        actual_end = start_to_end.get(end, end)

        # Check for loops or redundant segments
        if actual_start == actual_end:
            del end_to_start[actual_start]
            del start_to_end[actual_start]
            continue  # This segment forms a loop or is redundant, so skip it

        # Merge polylines or add new segment
        start_to_end[actual_start] = actual_end
        end_to_start[actual_end] = actual_start

        # Remove old references if they are now internal points of a polyline
        if start in end_to_start:
            del end_to_start[start]
        if end in start_to_end:
            del start_to_end[end]

    return start_to_end


# while there are some ends that need repair
while find_polyline_endpoints(segs):
    start_to_end = find_polyline_endpoints(segs)
    print(start_to_end)
    for start in start_to_end.keys():
        end = start_to_end[start]
        lines = []
        lines.extend(segs)
        pos = end
        # find the segment I am a part of
        my_seg = next(filter(lambda seg: seg[1] == pos, segs))
        # find all other segments
        other_segs = list(filter(lambda seg: seg[1] != pos, segs))

        # accum = 0
        # for seg in other_segs:
        #     accum += edge_start(seg, pos)
        #     accum += edge_end(seg, pos)
        # target = accum + math.pi*0
        target = math.pi

        angle_forward = get_direction(pos, other_segs, my_seg) + target + math.pi
        delta = angle_to_delta(angle_forward)
        closest_dist = 100000
        closest_pt = None
        for seg in segs:
            for x,y in seg:
                d = math.sqrt((y-pos[1])**2 + (x-pos[0])**2)
                if d < closest_dist and d != 0:
                    closest_dist = d
                    closest_pt = (x,y)
        # multiplier = closest_dist / 4
        multiplier = 1
        if closest_dist < 0.001:
            segs.append((pos, closest_pt))
            continue
        else:
            newpos = pos+(delta * multiplier)
            segs.append((pos, tuple(newpos)))


        for p1, p2 in lines:
            x_values = [p1[0], p2[0]]
            y_values = [p1[1], p2[1]]
            plt.plot(x_values, y_values, 'bo', linestyle="-")
        plt.show()


