import matplotlib.pyplot as plt
import numpy as np
import math

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

def edge_start(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (s1[1] - them_pt[1], s1[0] - them_pt[0])
    return math.atan2(*atansum(negatan(p1), angle))

def edge_end(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (s2[1] - them_pt[1], s2[0] - them_pt[0])
    return math.atan2(*atansum(p1, negatan(angle)))

def edge_start_baseline(me_seg):
    s1, s2 = me_seg
    angle = (s2[1] - s1[1], s2[0] - s1[0])
    return math.atan2(*angle)


def get_direction_backwards(pos, segs, dangling_start):
    accum = edge_start_baseline(dangling_start)
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)
    return accum


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


def grad(ox,oy,pt):
    px,py = pt
    x = ox - px
    y = oy - py
    gx = -((y)/(x**2 + y**2))
    gy = x/(x**2 + y**2)
    return (gx, gy)

def accum_grad_90(x, y, segs):
    ax = 0
    ay = 0
    for start, end in segs:
        # for pt in [start, end]:
        gx, gy = grad(x+0.00001,y+0.00001,start)
        ax += gy
        ay -= gx
        gx, gy = grad(x+0.00001,y+0.00001,end)
        ax -= gy
        ay += gx
    return (ax, ay)

def vecnorm(pt):
    x, y = pt
    dist = math.sqrt(x**2 + y**2)
    return (x / dist, y / dist)



start_to_end = find_polyline_endpoints(segs)
# print(start_to_end)

start = list(start_to_end.keys())[0]
end = start_to_end[start]
# find the segment I am a part of
my_seg = next(filter(lambda seg: seg[0] == start, segs))
# find all other segments
other_segs = list(filter(lambda seg: seg[0] != start, segs))
target = math.pi
angle_forward = get_direction_backwards(start, other_segs, my_seg) + target + math.pi
delta = angle_to_delta(angle_forward)
pos = start + (delta * 0.1)
plt.quiver(*start, *delta, color=['r','b','g'], scale=21)
for i in range(100):
    delt = vecnorm(accum_grad_90(*pos, segs))
    plt.plot([pos[0], pos[0] + delt[0]], [pos[1], pos[1] + delt[1]], 'bo', linestyle="-")
    pos += delt


# plt.imshow(background, aspect='auto', cmap='viridis', extent=[-20, 20, -20, 20], vmin=-math.pi, vmax=math.pi*2)

plt.show()