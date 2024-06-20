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

def negatan(f1):
    x,y = f1
    return x,-y

def subtract(s1, s2):
    return (s1[0] - s2[0], s1[1] - s2[1])

def add(s1, s2):
    return (s1[0] + s2[0], s1[1] + s2[1])

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

def winding_contour(pos,pt):
    x,y = subtract(pos, pt)
    dist = (x**2 + y**2)
    gx = x/dist
    gy = y/dist
    return (gx, gy)

def vecnorm(pt):
    x, y = pt
    dist = math.sqrt(x**2 + y**2)
    return (x / dist, y / dist)

def dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2 - y1)**2 + (x2 - x1)**2)

def find_initial_angle(my_seg, other_segs):
    start, end = my_seg
    accum = subtract(start, end)
    for seg in other_segs:
        s1, s2 = seg
        p1 = subtract(s1, end)
        p2 = subtract(s2, end)
        accum = atansum(accum, p1)
        accum = atansum(accum, negatan(p2))
        accum = vecnorm(accum)
    return np.array(accum)

def total_winding_contour(pos, segs):
    accum = (0,0)
    for start, end in segs:
        start_grad = winding_contour(pos, start)
        end_grad = winding_contour(pos, end)
        accum = subtract(accum, start_grad)
        accum = add(accum, end_grad)
    return vecnorm(accum)

def find_flow(start, ends, segs):
    # find the segment I am a part of
    my_seg = next(filter(lambda seg: seg[1] == start, segs))
    # find all other segments
    other_segs = list(filter(lambda seg: seg[1] != start, segs))
    delta = find_initial_angle(my_seg, other_segs)
    pos = start + (delta * 0.1)
    seg_outs = [(tuple(start), tuple(pos))]
    for _ in range(200):
        delt = total_winding_contour(pos, segs)
        seg_outs.append((tuple(pos), tuple(pos + delt)))
        pos += delt
        for end in ends:
            if dist(pos, end) < 1:
                seg_outs.append((tuple(pos), tuple(end)))
                return seg_outs

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
            for seg in self.original_segments:
                plt.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], 'bo', linestyle="-")
            plt.show()
        assert len(self.polylines) == 0

    def repair_segment(self):
        # Search starts at the end of a polyline
        start = self.polylines[0][-1]

        # Search will conclude when it finds the beginning of any polyline (including itself)
        endpoints = [polyline[0] for polyline in self.polylines]
        new_segs = find_flow(start, endpoints, self.original_segments)
        self.original_segments.extend(new_segs)
