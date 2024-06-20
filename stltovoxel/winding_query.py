import numpy as np
import matplotlib.pyplot as plt
import math

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

def atansum(f1, f2):
    x,y = f1
    w,z = f2
    return ( x*w - y*z, y*w + x*z,)

def edge_start(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = ( s1[0] - s2[0], s1[1] - s2[1],)
    p1 = ( s1[0] - them_pt[0],them_pt[1] - s1[1],)
    return atansum(p1, angle)

def edge_end(me_seg, them_pt):
    # Starter unpaired point
    s1, s2 = me_seg
    angle = ( s1[0] - s2[0], s2[1] - s1[1],)
    p1 = (s2[0] - them_pt[0], s2[1] - them_pt[1], )
    return atansum(p1, angle)

def subtract(s1, s2):
    angle = (s1[0] - s2[0], s1[1] - s2[1])
    return angle

def get_direction_backwards(pos, segs, dangling_start):
    accum = subtract(dangling_start[1], dangling_start[0])
    for seg in segs:
        accum = atansum(accum, edge_start(seg, pos))
        accum = atansum(accum, edge_end(seg, pos))
        accum = vecnorm(accum)
    return accum

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
        gx, gy = grad(x,y,start)
        ax += gy
        ay -= gx
        gx, gy = grad(x,y,end)
        ax -= gy
        ay += gx
    return (ax, ay)

def vecnorm(pt):
    x, y = pt
    dist = math.sqrt(x**2 + y**2)
    return (x / dist, y / dist)

def dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2 - y1)**2 + (x2 - x1)**2)

def find_initial_angle(start, other_segs, my_seg):
    delta_x, delta_y = get_direction_backwards(start, other_segs, my_seg)
    delta = np.array([delta_x, delta_y])
    return delta

def grad_90_norm(pos, segs):
    delt = vecnorm(accum_grad_90(*pos, segs))
    return delt

def find_flow(start, ends, segs):
    for seg in segs:
        plt.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], 'bo', linestyle="-")

    # find the segment I am a part of
    my_seg = next(filter(lambda seg: seg[0] == start, segs))
    # find all other segments
    other_segs = list(filter(lambda seg: seg[0] != start, segs))
    delta = find_initial_angle(start, other_segs, my_seg)
    pos = start + (delta * 0.1)
    for _ in range(200):
        delt = grad_90_norm(pos, segs)
        plt.plot([pos[0], pos[0] + delt[0]], [pos[1], pos[1] + delt[1]], 'bo', linestyle="-")
        pos += delt
        for end in ends:
            print(pos, end, dist(pos, end))
            if dist(pos, end) < 1:
                plt.show()
                return end

    plt.show()
    raise "Flow not found"

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
            assert old_seg_length - 1 == len(self.polylines)
        assert len(self.polylines) == 0

    def repair_segment(self):
        # Search starts at the end of a polyline
        start = self.polylines[0][0]

        # Search will conclude when it finds the beginning of any polyline (including itself)
        endpoints = [polyline[-1] for polyline in self.polylines]
        end = find_flow(start, endpoints, self.original_segments)
        print(self.original_segments)
        new_segment = (end, start)
        print(new_segment)
        self.original_segments.append(new_segment)
