import numpy as np
import math
import functools
from queue import PriorityQueue
import matplotlib.pyplot as plt


def find_polylines(segments):  # noqa: C901
    polylines = []
    segment_forward_dict = {}
    segment_backward_dict = {}

    # create a dictionary where each endpoint is a key, and the value is a list of segments
    for segment in segments:
        start, end = segment
        if start not in segment_forward_dict:
            segment_forward_dict[start] = []
        segment_forward_dict[start].append(end)
        if end not in segment_backward_dict:
            segment_backward_dict[end] = []
        segment_backward_dict[end].append(start)
    # loop through each segment, and recursively add connected segments to form polylines
    while len(segment_forward_dict) > 0:
        start = list(segment_forward_dict.keys())[0]
        polyline = [start]

        # Iterate through forward dict
        while True:
            if start not in segment_forward_dict:
                break
            next_points = segment_forward_dict[start]
            end = next_points[0]

            segment_forward_dict[start].remove(end)
            if len(segment_forward_dict[start]) == 0:
                del segment_forward_dict[start]
            segment_backward_dict[end].remove(start)
            if len(segment_backward_dict[end]) == 0:
                del segment_backward_dict[end]
            # Append points to the end of the list
            polyline.append(end)
            start = end

        # Reset the start point
        start = polyline[0]
        # Iterate through backward dict
        while True:
            if start not in segment_backward_dict:
                break
            next_points = segment_backward_dict[start]
            end = next_points[0]

            segment_backward_dict[start].remove(end)
            if len(segment_backward_dict[start]) == 0:
                del segment_backward_dict[start]
            segment_forward_dict[end].remove(start)
            if len(segment_forward_dict[end]) == 0:
                del segment_forward_dict[end]

            # Insert points at the front of the list
            polyline.insert(0, end)
            start = end
        polylines.append(polyline)

    return polylines


def closest_distance(point, goals):
    return min([dist(point, goal) for goal in goals])


def dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2 - y1)**2 + (x2 - x1)**2)


def normalize(num):
    return ((num + math.pi) % (2*math.pi)) - math.pi


def signed_point_line_dist(line, point):
    a, b = line
    x1, y1 = a
    x2, y2 = b
    x0, y0 = point
    num = ((x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1))
    denom = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / denom


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
    y, x = accum
    return vecnorm((x,y))

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
    return np.array([pt[0]/dist, pt[1]/dist])

def dist(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def follow_flow(segs, start, goals):
    my_seg = next(filter(lambda seg: seg[1] == start, segs))
    other_segs = list(filter(lambda seg: seg[1] != start, segs))
    delta = get_direction(start, other_segs, my_seg)
    pos = start + (delta * 0.0001)
    path = [(tuple(start), tuple(pos))]

    last_dist = 0.00001
    for _ in range(250):
        delt = vecnorm(accum_grad_zero(pos, segs)) * (last_dist * .1)
        path.append((tuple(pos), tuple(pos+delt)))
        pos += delt
        last_dist = dist(goals[0], pos)
        for goal in goals:
            d = dist(goal, pos)
            last_dist = min(last_dist, d)
            if d < .0001:
                print(f"found endpoint {goal}")
                path.append((tuple(pos), tuple(goal)))
                return path
    raise Exception("ran out of iterations")

class WindingQuery():
    def __init__(self, segments):
        # Maps endpoints to the polygon they form
        self.loops = []
        # Populate initially
        self.polylines = []
        self.original_segments = segments
        self.collapse_segments()

    def collapse_segments(self):
        self.loops = []
        self.polylines = []
        for polyline in find_polylines(self.original_segments):
            if polyline[0] == polyline[-1]:
                self.loops.append(polyline)
            else:
                self.polylines.append(polyline)

    def repair_all(self):
        while self.polylines:
            self.repair_segment()
            old_seg_length = len(self.polylines)
            self.collapse_segments()
            # assert old_seg_length - 1 == len(self.polylines)
        assert len(self.polylines) == 0

    def repair_segment(self):
        # Search starts at the end of a polyline
        start = self.polylines[0][-1]

        # Search will conclude when it finds the beginning of any polyline (including itself)
        goals = [polyline[0] for polyline in self.polylines]
        more_path = follow_flow(self.original_segments, start, goals)

        # new_segment = (start, end)
        self.original_segments.extend(more_path)

