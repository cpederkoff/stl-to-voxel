import numpy as np
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


def atan_sum(f1, f2):
    # Atan sum identity
    # atan2(atan_sum(f1, f2)) == atan2(f1) + atan2(f2)
    x1, y1 = f1
    x2, y2 = f2
    return (x1*x2 - y1*y2, y1*x2 + x1*y2)


def atan_diff(f1, f2):
    # Atan difference identity
    # atan2(atan_diff(f1, f2)) == atan2(f1) - atan2(f2)
    x1, y1 = f1
    x2, y2 = f2
    return (x1*x2 + y1*y2, y1*x2 - x1*y2)


def subtract(s1, s2):
    return (s1[0] - s2[0], s1[1] - s2[1])


def add(s1, s2):
    return (s1[0] + s2[0], s1[1] + s2[1])


def winding_contour_pole(pos, pt, repel):
    # The total winding number of a system is composed of a sum of atan2 functions (one at each point of each line segment)
    # The gradient of atan2(y, x) is
    # Gx = -y/(x^2+y^2); Gy = x/(x^2+y^2)
    # The contour (direction of no increase) is orthogonal to the gradient, either
    # (-Gy, Gx) or (Gy, -Gx)
    # This is represented by:
    # Cx =  x/(x^2+y^2); Cy =  y/(x^2+y^2) or
    # Cx = -x/(x^2+y^2); Cy = -y/(x^2+y^2)
    # In practice, one of each is used per line segment which repels & attracts the vector field.
    x, y = subtract(pos, pt)
    dist2 = (x**2 + y**2)
    cx = x/dist2
    cy = y/dist2
    if repel:
        return (cx, cy)
    else:
        return (-cx, -cy)


def normalize(pt):
    x, y = pt
    dist = math.sqrt(x**2 + y**2)
    return (x / dist, y / dist)


def distance_squared(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return (y2 - y1)**2 + (x2 - x1)**2


def initial_direction(pt, polyline_endpoints):
    # Computing the winding number of a given point requires 2 angle computations per line segment (one per point).
    # This method makes 2 angle computations for every segment in other_segs to compute the winding number at my_seg[1].
    # It also makes one angle computation from my_seg[0] to my_seg[1].
    # The result is an angle out of my_seg which leads to a winding number of a target value.
    # In theory this target winding number can be any value, but here pi radians (180 degrees) is used for simplicity.
    # Also, generally angle computation would take the form of [atan2(start-pt)-atan2(end-pt)]+... , but multiple atan2 calls
    # can be avoided through use of atan2 identities.
    # Since the final angle would be converted back into a vector, no atan2 call is required.
    accum = (1, 0)
    for start, end in polyline_endpoints:
        # Low quality meshes may have multiple segments with the same start or end point, so we should not attempt
        # to compute the angle from pt because the result is undefined.
        if start != pt:
            accum = atan_sum(accum, subtract(start, pt))
        if end != pt:
            # This will trigger for at least one segment because pt is the end of a polyline.
            accum = atan_diff(accum, subtract(end, pt))
        # Without this, accum can get arbitrarily large and lead to floating point problems
        accum = normalize(accum)
    return np.array(accum)


def winding_contour(pos, segs):
    accum = (0, 0)
    for start, end in segs:
        # Starting points attract the vector field
        start_vec = winding_contour_pole(pos, start, repel=False)
        accum = add(accum, start_vec)
        # Ending points repel the vector field
        end_vec = winding_contour_pole(pos, end, repel=True)
        accum = add(accum, end_vec)
    return normalize(accum)


def winding_number_search(start, ends, polyline_endpoints, max_iterations):
    # Find the initial direction to start marching towards.
    # As an optimization, polyline endpoints are used instead of original_segments for initial_direction because
    # start and end points in the same place cancel out.
    direction = initial_direction(start, polyline_endpoints)
    # Move slightly toward that direction to pick the contour that we will use below
    pos = start + (direction * 0.1)
    for _ in range(max_iterations):
        # Flow lines in this vector field have equivalent winding numbers
        # As an optimization, polyline endpoints are used instead of original_segments for winding_contour because
        # start and end points in the same place cancel out.
        direction = winding_contour(pos, polyline_endpoints)
        # March along the flowline to find where it terminates.
        pos = pos + direction
        # It should terminate at an endpoint
        for end in ends:
            if distance_squared(pos, end) < 1:
                return end

    raise Exception("Failed to repair mesh")


class PolygonRepair():
    def __init__(self, segments, dimensions):
        # Maps endpoints to the polygon they form
        self.loops = []
        # Populate initially
        self.polylines = []
        self.original_segments = segments
        self.dimensions = dimensions
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
            self.repair_polyline()
            old_seg_length = len(self.polylines)
            self.collapse_segments()
            assert old_seg_length - 1 == len(self.polylines)
        assert len(self.polylines) == 0

    def repair_polyline(self):
        # Search starts at the end of an arbitrary polyline
        search_start = self.polylines[0][-1]
        # Search will conclude when it finds the beginning of any polyline (including itself)
        search_ends = [polyline[0] for polyline in self.polylines]
        polyline_endpoints = [(polyline[0], polyline[-1]) for polyline in self.polylines]
        max_iterations = self.dimensions[0] + self.dimensions[1]
        end = winding_number_search(search_start, search_ends, polyline_endpoints, max_iterations)
        self.original_segments.append((search_start, end))
