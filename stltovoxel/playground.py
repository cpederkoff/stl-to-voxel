import matplotlib.pyplot as plt
import numpy as np
import math

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

def edge_start_baseline(s1, s2):
    return (s1[1] - s2[1], s1[0] - s2[0])

def edge_start(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = edge_start_baseline(s1, s2)
    p1 = (s1[1] - them_pt[1], s1[0] - them_pt[0])
    return atansum(negatan(p1), angle)

def edge_end(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = edge_start_baseline(s1, s2)
    p1 = (s2[1] - them_pt[1], s2[0] - them_pt[0])
    return atansum(p1, negatan(angle))


def get_direction(pos, segs, dangling_start):
    accum = edge_start_baseline(dangling_start[1], dangling_start[0])
    for seg in segs:
        accum = atansum(accum, edge_start(seg, pos))
        accum = atansum(accum, edge_end(seg, pos))
    return math.atan2(*accum)


def angle_to_delta(theta):
    delta_x = math.cos(theta)
    delta_y = math.sin(theta)
    return np.array([delta_x, delta_y])

segs = [
    ((0,0),(20,0)),
    ((20,10),(0,10)),
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


def grad_zero(pos, monopole, repel=True):
    dir = pos - monopole
    denom = (dir[0]**2 + dir[1]**2)
    grad = dir / denom
    if repel:
        return grad
    else:
        return -grad
    
def accum_grad_zero(pt, segs):
    acc = np.array([0.0,0.0])
    for start, end in segs:
        acc += grad_zero(pt,start, repel=True)
        acc += grad_zero(pt,end, repel=False)
    return acc

def vecnorm(pt):
    dist = math.sqrt(pt[0]**2 + pt[1]**2)
    return pt/dist

start_to_end = find_polyline_endpoints(segs)

start = list(start_to_end.keys())[0]
my_seg = next(filter(lambda seg: seg[0] == start, segs))
# find all other segments
other_segs = list(filter(lambda seg: seg[0] != start, segs))
angle_forward = get_direction(start, other_segs, my_seg)
delta = angle_to_delta(angle_forward)
print(delta)
pos = start + (delta * 0.0001)

plt.quiver(*start, *delta, color=['r','b','g'], scale=21)
for i in range(10):
    delt = vecnorm(accum_grad_zero(pos, segs))
    plt.quiver(*pos, *(delt), color=['r','b','g'], scale=21)
    plt.plot([pos[0], pos[0] + delt[0]], [pos[1], pos[1] + delt[1]], 'bo', linestyle="-")
    pos += delt

plt.show()
