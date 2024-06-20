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

def edge_start(start, them_pt):
    return (start[1] - them_pt[1], start[0] - them_pt[0])

def edge_end(other, them_pt):
    return other[1] - them_pt[1], other[0] - them_pt[0]

def get_direction(pos, segs, dangling_start):
    accum = edge_start_baseline(dangling_start[0], dangling_start[1])
    for seg in segs:
        accum = atansum(accum, edge_start(seg[1], pos))
        accum = atansum(accum, edge_end(seg[0], pos))
    return math.atan2(*accum)

def angle_to_delta(theta):
    delta_x = math.cos(theta)
    delta_y = math.sin(theta)
    return np.array([delta_x, delta_y])

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
        acc += grad_zero(pt,start, repel=False)
        acc += grad_zero(pt,end, repel=True)
    return acc

def vecnorm(pt):
    dist = math.sqrt(pt[0]**2 + pt[1]**2)
    return pt/dist

def dist(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

segs = [
    ((0,0),(10,10)),
    ((10,20), (0,10)),
]
for start, end in segs:
    plt.plot([start[0], end[0]], [start[1], end[1]], 'bo', linestyle="-")

start = segs[0][1]
my_seg = next(filter(lambda seg: seg[1] == start, segs))
other_segs = list(filter(lambda seg: seg[1] != start, segs))
angle_forward = get_direction(start, other_segs, my_seg)
delta = angle_to_delta(angle_forward)
pos = start + (delta * 0.0001)

plt.quiver(*start, *delta, color=['r','b','g'], scale=21)
for i in range(25):
    delt = vecnorm(accum_grad_zero(pos, segs))
    plt.quiver(*pos, *(delt), color=['r','b','g'], scale=21)
    plt.plot([pos[0], pos[0] + delt[0]], [pos[1], pos[1] + delt[1]], 'bo', linestyle="-")
    pos += delt
    for start, end in segs:
        if dist(end, pos) < 1:
            print(f"found endpoint {end}")

plt.show()
