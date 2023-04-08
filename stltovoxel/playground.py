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
# 
def is_right(line, point):
    a, b = line
    x1, y1 = a
    x2, y2 = b
    x0, y0 = point
    num = ((x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1))
    return num > 0

def corners(segs):
    im = np.zeros((100,100))
    for i in range(len(segs) - 1):
        # pdb.set_trace()

        s1 = segs[i]
        s2 = segs[i+1]
        assert s1[1] == s2[0]
        a = np.array(list(s1[0]))
        b = np.array(list(s1[1]))
        c = np.array(list(s2[1]))
        l1 = a - b
        l2 = b - c
        # pdb.set_trace()
        
        ang = math.atan2(*atandiff((l2[1], l2[0]), (l1[1], l1[0])))
        
        for x in range(-50, 50):
            for y in range(-50, 50):
                
                if ang < 0 : 
                    # Concave case 
                    if not is_right((a, b), (x,y)) and not is_right((c, b), (x,y)):
                        im[y+50][x+50] += ang + 2 * math.pi
                    else: 
                        im[y+50][x+50] += ang 
                else :
                    # Convex case (normal)
                    if is_right((a, b), (x,y)) and is_right((c, b), (x,y)):
                        im[y+50][x+50] += ang - 2 * math.pi
                    else: 
                        im[y+50][x+50] += ang 
    return im


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
    

def line(segs, inc):
    im = np.zeros((100,100))
    for x in range(-50, 50):
        for y in range(-50, 50):
            answers = []
            for p1, p2 in segs:
                x1, y1 = p1
                x2, y2 = p2
                angle = (y2 - y1, x2 - x1)
                # angle = (0,0)
                p1 = (y-y1, x-x1)
                   
                p2 = (y-y2, x-x2)
                answers.append(atansum(negatan(p1), angle))
                answers.append(atansum(p2, negatan(angle)))
                # answers.append(atansum(
                #     atansum(p1, negatan(angle)),
                #     atansum(negatan(p2), angle),
                #     )
                # )
                # answers.append(-normalize(math.atan2(y-y2, x-x2) - angle))
            accum = 0
            for i in inc:
                accum += math.atan2(*answers[i])

            im[y+50][x+50] = accum
    return im

def grad(x, y):
    dist2 = (x**2 + y**2)
    if dist2 == 0:
        return np.array([0,0])
    dx = -y/dist2
    dy = x/dist2
    return np.array([dx, dy])

def vecs(segs):
    Xs = np.zeros((100,100))
    Ys = np.zeros((100,100))
    for x in range(-50, 50):
        for y in range(-50, 50):
            answers = []
            for p1, p2 in segs:
                x1, y1 = p1
                x2, y2 = p2
                angle = grad(y2-y1, x2-x1)
                answers.append(grad(y-y1, x-x1)-angle)
                # answers.append(-grad(y-y2, x-x2)-angle)
            for i in range(len(answers)):
                # pdb.set_trace()
                # print(answers[i])
                dx, dy = answers[i].tolist()
                Xs[y+50][x+50] += dx
                Ys[y+50][x+50] += dy

    return Xs, Ys
    

segs = [
    ((-30,0),(-10,-10)),
    ((-10,-10), (10,-15)),
    ((10,-15), (0,-30)),
    # ((20,-10), (40,-10))
    # ((0,20), (30,20)),
]
fig, axs = plt.subplots(2, 4)
print(edge_start(segs[0], segs[-1][-1]))
print(edge_end(segs[-1], segs[0][0]))

axs[0,0].imshow(line(segs, [0]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
axs[0,1].imshow(line(segs, [5]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
axs[0,2].imshow(line(segs, [1,2,3,4]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
axs[0,3].imshow(line(segs, [0,1,2,3,4,5]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
axs[1,2].imshow(corners(segs), origin='lower', vmin=-math.pi, vmax=2*math.pi)
axs[1,3].imshow(corners(segs) + line(segs, [0,-1]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
# axs[0,1].imshow(line(antiseg, [0,1]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
# axs[1,0].imshow(line(segs, [0,1,2,3,4,5]) - line(segs, [0,5]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
# axs[1,1].imshow(line(segs, [0,1]), origin='lower', vmin=-math.pi, vmax=2*math.pi)
# gx, gy = np.gradient(line(segs, [0,1,2,3]))
# plt.quiver(gx, gy)

# axs[1, 0].imshow(line(segs, [2,3]), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[2, 0].imshow(line(segs, [4,5]), origin='lower', vmin=-math.pi, vmax=math.pi)

# axs[0, 1].imshow(line(segs, [0, 5]), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[1, 1].imshow(line(segs, [1, 2]), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[2, 1].imshow(line(segs, [3, 4]), origin='lower', vmin=-math.pi, vmax=math.pi)

# axs[0, 2].imshow(line(segs, [0,1,2,3]), origin='lower', vmin=-math.pi, vmax=math.pi)

# axs[0, 2].imshow(line(segs, [1,2,3]), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[1, 2].imshow(line(segs, [0,1,2]), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[2, 2].imshow(line(segs, [0,1,2,3]), origin='lower', vmin=-math.pi, vmax=math.pi)

# axs[1].imshow(line((0,0),(0,30)), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[2].imshow(line((0,0),(30,30)), origin='lower', vmin=-math.pi, vmax=math.pi)
# axs[3].imshow(line((0,0),(30,-30)), origin='lower', vmin=-math.pi, vmax=math.pi)

plt.show()
