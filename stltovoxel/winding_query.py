import numpy as np
import matplotlib.pyplot as plt
import math
import functools
from queue import PriorityQueue
import pdb
import matplotlib.pyplot as plt
import time

def find_polylines(segments):
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

      segment_backward_dict.get(start).remove(end)
      if len(segment_backward_dict[start]) == 0:
        del segment_backward_dict[start]
      segment_forward_dict.get(end).remove(start)
      if len(segment_forward_dict[end]) == 0:
        del segment_forward_dict[end]

      # Insert points at the front of the list
      polyline.insert(0, end)
      start = end
    polylines.append(polyline)

  return polylines

class WindingQuery():
  def __init__(self, segments):
    self.atans = 0
    # Maps endpoints to the polygon they form
    self.loops = []
    # Populate initially
    self.segments = []
    # pdb.set_trace()
    self.original_segments = [[tuple(pt.tolist())[:2] for pt in seg] for seg in segments]
    self.collapse_segments()
    
  def collapse_segments(self):
    self.loops = []
    self.segments = []
    for polyline in find_polylines(self.original_segments):
      if polyline[0] == polyline[-1]:
        self.loops.append(polyline)
      else:
        self.segments.append(polyline)

  def normalize(self, num): 
    return ((num + math.pi) % (2*math.pi)) - math.pi

  def winding(self, segment, point):
    i,j = point

    start, end = segment

    start = np.array(list(start))
    end = np.array(list(end))
    me = np.array(point)
    
    # Side 1
    me_offset = me - start
    my_ang1 = math.atan2(me_offset[1], me_offset[0])
    # Side 2
    me_offset = me - end
    my_ang2 = math.atan2(me_offset[1], me_offset[0])
    self.atans += 2
    # 180 - other angles gives us angle seen by point
    return self.normalize(my_ang2 - my_ang1)

  def signedPointLineDist(self, line, point):
    a, b = line
    x1, y1 = a
    x2, y2 = b
    x0, y0 = point
    num = ((x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1)) 
    # return num
    # Not needed
    denom = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / denom
  
  def query_winding(self, point):
    total = 0
    for polyline in self.segments:
      total += self.winding_segment(polyline, point)
    return total

  def dist(self, p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((y2 - y1)**2 + (x2 - x1)**2)

  def close_to_goal(self, start, goals):
    sx, sy = start
    for goal in goals:
      gx, gy = goal
      if abs(sx-gx) <= 1 and abs(sy-gy) <= 1:
        return goal
    return False

  def astar(self, start, goals, heuristic):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    current = None
    while not frontier.empty():
      score, current = frontier.get()
      close_goal = self.close_to_goal(current, goals)
      if close_goal:
        came_from[close_goal] = current
        current = close_goal
        break

      for dx in range(-1,2):
        for dy in range(-1,2):
          next_point = (current[0] + dx, current[1] + dy)
          new_cost = cost_so_far[current] + abs(self.query_winding(next_point) - math.pi) * 100

          if next_point not in cost_so_far or new_cost < cost_so_far[next_point]:
            cost_so_far[next_point] = new_cost
            priority = new_cost + heuristic(next_point, goals)
            frontier.put((priority, next_point))
            came_from[next_point] = current

    path = []
    # Current is now one of the goals
    assert current is not None
    while current != start:
      path.append(current)
      current = came_from[current]
    path.append(start)
    path.reverse()
    # self.chart_self(path)
    return path[-1]


  def repair_segment(self, start):
    endpoints = []
    for polyline in self.segments:
      endpoints.append(polyline[0])
      endpoints.append(polyline[-1])
    endpoints.remove(start)
    def heuristic(next_point, goals):
      return abs(min([self.dist(next_point, goal) for goal in goals]))
    return self.astar(start, endpoints, heuristic)
  
  def repair_all(self):
    while len(self.segments) > 0:
      # Find the point after the segment end (will be in the list of endpoints)
      start = self.segments[0][-1]
      end = self.repair_segment(start)
      self.original_segments.append((start, end))
      self.collapse_segments()
    assert len(self.segments) == 0

  # @functools.cache
  def getLines(self, polyline):
    start = np.array(polyline[0])
    end = np.array(polyline[-1])
    slope = end - start

    furthest_in = 0
    innermost = polyline[0]
    furthest_out = 0
    outermost = polyline[0]
    for pt in polyline:
      dist = self.signedPointLineDist((polyline[0], polyline[-1]), pt)
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

  def winding_segment(self, polyline, point):
    collapsed = (polyline[0], polyline[-1])
    inner_line, outer_line = self.getLines(polyline)

    if len(polyline) == 2:
      # This is the actual segment so okay to be behind it.
      return self.winding(collapsed, point)
    elif self.signedPointLineDist(inner_line, point) < 0:
      # We are inside and beyond any concavity
      return self.winding(collapsed, point)
    elif self.signedPointLineDist(outer_line, point) > 0:
      # We are outside beyond any convexity
      return self.winding(collapsed, point)
    else:
      split = int(len(polyline) / 2)
      # Otherwise, split the segment
      return self.winding_segment(polyline[:split+1], point) + self.winding_segment(polyline[split:], point)

if __name__ == "__main__":
  segments3 = [
  [(10,10), (20,10)],
  [(20,10), (30,10)],
  # [(30,10), (40,10)],
  [(40,10), (30,20)],
  [(30,20), (40,40)],
  # [(40,40), (10,40)],
  [(10,40), (10,10)],
]
  quer = WindingQuery(segments3)

  quer.repair_all()

  # Create a new figure
  fig = plt.figure()

  # Add a subplot to the figure
  ax = fig.add_subplot(1, 1, 1)

  # Plot the polyline using the x and y coordinates
  for loop in quer.loops:
    ax.plot(*zip(*loop))

  # Add labels and title to the plot
  ax.set_xlabel('X-axis')
  ax.set_ylabel('Y-axis')
  ax.set_title('Polyline Plot')

  # Display the plot
  plt.show()

  