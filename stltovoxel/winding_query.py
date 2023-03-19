import numpy as np
import math
import functools
from queue import PriorityQueue


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


def close_to_goal(start, goals):
    sx, sy = start
    for goal in goals:
        gx, gy = goal
        if abs(sx-gx) <= 1 and abs(sy-gy) <= 1:
            return goal
    return False


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
        start = self.polylines[0][-1]

        # Search will conclude when it finds the beginning of any polyline (including itself)
        endpoints = [polyline[0] for polyline in self.polylines]
        end = self.a_star(start, endpoints)

        new_segment = (start, end)
        self.original_segments.append(new_segment)

    def a_star(self, start, goals):
        frontier = PriorityQueue()
        frontier.put((0, start))
        cost_so_far = {start: 0}

        current = None
        while not frontier.empty():
            score, current = frontier.get()
            close_goal = close_to_goal(current, goals)
            if close_goal:
                current = close_goal
                break

            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    next_point = (current[0] + dx, current[1] + dy)
                    heuristic_cost = closest_distance(next_point, goals)
                    new_cost = cost_so_far[current] + abs(self.query_winding(next_point) - math.pi) * 200

                    if next_point not in cost_so_far or new_cost < cost_so_far[next_point]:
                        cost_so_far[next_point] = new_cost
                        priority = new_cost + heuristic_cost
                        frontier.put((priority, next_point))
        assert current is not None
        return current

    def query_winding(self, point):
        total = 0
        for polyline in self.polylines:
            total += self.winding_segment(polyline, point)
        return total

    def winding_segment(self, polyline, point):
        collapsed = (polyline[0], polyline[-1])
        inner_line, outer_line = self.get_lines(tuple(polyline))

        if len(polyline) == 2:
            # This is the actual segment so okay to be behind it.
            return self.winding(collapsed, point)
        elif signed_point_line_dist(inner_line, point) < 0:
            # We are inside and beyond any concavity
            return self.winding(collapsed, point)
        elif signed_point_line_dist(outer_line, point) > 0:
            # We are outside beyond any convexity
            return self.winding(collapsed, point)
        else:
            split = int(len(polyline) / 2)
            # Otherwise, split the segment
            return self.winding_segment(polyline[:split+1], point) + self.winding_segment(polyline[split:], point)

    def winding(self, segment, point):
        start, end = segment
        start = np.array(start)
        end = np.array(end)
        point = np.array(point)
        # Side 1
        offset = point - start
        ang1 = math.atan2(offset[1], offset[0])
        # Side 2
        offset = point - end
        ang2 = math.atan2(offset[1], offset[0])
        return normalize(ang2 - ang1)

    @functools.lru_cache(maxsize=None)
    def get_lines(self, polyline):
        start = np.array(polyline[0])
        end = np.array(polyline[-1])
        slope = end - start

        furthest_in = 0
        innermost = polyline[0]
        furthest_out = 0
        outermost = polyline[0]
        for pt in polyline:
            dist = signed_point_line_dist((polyline[0], polyline[-1]), pt)
            if dist < furthest_in:
                innermost = pt
                furthest_in = dist
            elif dist > furthest_out:
                outermost = pt
                furthest_out = dist
        innermost = np.array(innermost)
        outermost = np.array(outermost)
        inner_line = (innermost, innermost + slope)
        outer_line = (outermost, outermost + slope)
        return inner_line, outer_line
