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
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (s1[1] - them_pt[1], s1[0] - them_pt[0])
    return math.atan2(*atansum(negatan(p1), angle))

def edge_start_no_atan(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = (s1[1] - s2[1], s1[0] - s2[0])
    p1 = (s1[1] - them_pt[1], s1[0] - them_pt[0])
    return atansum(negatan(p1), angle)

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

def edge_end_baseline(me_seg):
    s1, s2 = me_seg
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

def get_winding(pos, segs):
    accum = 0
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)
    return accum

def get_direction(pos, segs, dangling_end):
    accum = 0
    for seg in segs:
        accum += edge_start(seg, pos)
        accum += edge_end(seg, pos)
    # accum += edge_start(dangling_end, pos)

    base = edge_end_baseline(dangling_end)
    return base - accum

def get_direction_backwards(pos, segs, dangling_start):
    accum = 0
    for seg in segs:
        accum -= edge_start(seg, pos)
        accum -= edge_end(seg, pos)
    # accum += edge_start(dangling_end, pos)

    base = edge_start_baseline(dangling_start)
    return base - accum

def get_direction_iter(pos, segs, dangling_end, target):
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
    ((0,0),(20,0)),
    ((20,10),(0,10)),
    # ((0,2.5),(0,7.5)),
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

background = np.zeros((200,200))
for posxa in range(200):
    for posya in range(200):
        posx = (posxa - 100) * 0.2
        posy = (posya - 100) * 0.2
        winding = get_winding((posx, posy), segs)
        if abs(winding - math.pi) < .1:
            winding = math.pi*2
        background[199-posya][posxa] = winding

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

# cx, cy = -.5,0
# for i in range(200):
#     # calculate gradient for current position
#     mgx, mgy = vecnorm(accum_grad_90(cx, cy, segs))
#     # move forward
#     mgxnorm = mgx * 0.1
#     mgynorm = mgy * 0.1
#     plt.plot([cx, cx + mgxnorm], [cy, cy + mgynorm], 'bo', linestyle="-")
#     cx += mgxnorm
#     cy += mgynorm
#     # add back segment
for x in range(-10,10):
    for y in range(-10,10):
        ax, ay = accum_grad_90(x,y,segs)
        plt.quiver(x,y, ax, ay, color=['r','b','g'], scale=21)




    


# while there are some ends that need repair
# while find_polyline_endpoints(segs):
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
# plt.quiver(*start, *delta, color=['r','b','g'], scale=21)
for i in range(100):
    delt = vecnorm(accum_grad_90(*pos, segs))
    plt.plot([pos[0], pos[0] + delt[0]], [pos[1], pos[1] + delt[1]], 'bo', linestyle="-")
    pos += delt


plt.imshow(background, aspect='auto', cmap='viridis', extent=[-20, 20, -20, 20], vmin=-math.pi, vmax=math.pi*2)

plt.show()