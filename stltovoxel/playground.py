import matplotlib.pyplot as plt
import numpy as np
import math

def atan_sum(f1, f2):
    y, x = f1
    z, w = f2
    return (y*w + x*z, x*w - y*z)

def atan_neg(f1):
    y,x = f1
    return -y, x

def edge_start(me_seg, them_pt):
    s1, s2 = me_seg
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (s1[1] - them_pt[1], s1[0] - them_pt[0])
    return math.atan2(*atan_sum(atan_neg(p1), angle))

def edge_end(me_seg, them_pt):
    s1, s2 = me_seg
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (s2[1] - them_pt[1], s2[0] - them_pt[0])
    return math.atan2(*atan_sum(p1, atan_neg(angle)))

def edge_start_baseline(me_seg):
    s1, s2 = me_seg
    angle = (s2[1] - s1[1], s2[0] - s1[0])
    return math.atan2(*angle)

def edge_end_baseline(me_seg):
    s1, s2 = me_seg
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    return math.atan2(*angle)

def get_winding(pos, segs):
    accum = 0
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)
    return accum

def get_angle(pos, segs, dangling_end, target):
    accum = 0
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)

    base = edge_end_baseline(dangling_end)
    return (base - accum) + target + math.pi

def get_angle_backwards(pos, segs, dangling_start, target):
    accum = 0
    for seg in segs:
        accum -= edge_start(seg, pos)
        accum -= edge_end(seg, pos)

    base = edge_start_baseline(dangling_start)
    return (base - accum) + target + math.pi

def angle_to_delta(theta):
    delta_x = math.cos(theta)
    delta_y = math.sin(theta)
    return np.array([delta_x, delta_y])

def grad(ox,oy,pt):
    px,py = pt
    x = ox - px
    y = oy - py
    gx = -y/(x**2 + y**2)
    gy = x/(x**2 + y**2)
    return (gx, gy)

def contour_left(ox, oy, pt):
    gx, gy = grad(ox, oy, pt)
    return (-gy, gx)

def contour_right(ox, oy, pt):
    gx, gy = grad(ox, oy, pt)
    return (gy, -gx)

def sum_contour(x, y, segs):
    ax = 0
    ay = 0
    for start, end in segs:
        # Adding 0.00001 to avoid undefined errors due to finding contour eactly on a segment point
        cx, cy = contour_right(x+0.00001,y+0.00001,start)
        ax += cx
        ay += cy
        cx, cy = contour_left(x+0.00001,y+0.00001,end)
        ax += cx
        ay += cy
    return (ax, ay)

def vecnorm(pt):
    x, y = pt
    dist = math.sqrt(x**2 + y**2)
    return (x / dist, y / dist)

segs = [
    ((0,10),(0,0)),
    ((0,0),(10,0)),
    ((10,5),(5,10)),
]

background = np.zeros((200,200))
for posxa in range(200):
    for posya in range(200):
        posx = (posxa - 100) * 0.2
        posy = (posya - 100) * 0.2
        winding = get_winding((posx, posy), segs)
        if abs(winding - math.pi) < .1:
            winding = math.pi*2
        background[199-posya][posxa] = winding

for x in range(-20,20, 1):
    for y in range(-20,20, 1):
        ax, ay = sum_contour(x,y,segs)
        if abs(ax) > 1000 or abs(ay) > 1000:
            continue
        plt.quiver(x,y, ax, ay, color=['r'], scale=21)

start = segs[0][0]
end = segs[0][1]
# find the segment I am a part of
my_seg = next(filter(lambda seg: seg[0] == start, segs))
# find all other segments
other_segs = list(filter(lambda seg: seg[0] != start, segs))
angle_forward = get_angle_backwards(start, other_segs, my_seg, math.pi) 
delta = angle_to_delta(angle_forward)
pos = start + (delta * 0.1)
plt.quiver(*start, *delta, color=['g'], scale=21)
for i in range(100):
    delt = vecnorm(sum_contour(*pos, segs))
    plt.plot([pos[0], pos[0] + delt[0]], [pos[1], pos[1] + delt[1]], 'bo', linestyle="-")
    pos += delt


plt.imshow(background, aspect='auto', cmap='viridis', extent=[-20, 20, -20, 20], vmin=-math.pi, vmax=math.pi*2)

plt.show()