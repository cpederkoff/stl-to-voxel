import numpy as np
import matplotlib.pyplot as plt
import math
import functools
class WindingQuery():
  def __init__(self, segments):
    self.atans = 0
    # Maps endpoints to the polygon they form
    self.collapsed_segments = {}
    # Populate initially
    for segment in segments:
      # Segments come in as a numpy array of:
      # length = 3 numpy arrays 
      start, end = segment
      segment = (tuple(start[:2]), tuple(end[:2]))
      self.collapsed_segments[segment] = segment

    did_something = True
    while did_something:
      did_something = False
      segments = list(self.collapsed_segments.keys()).copy()
      for seg1 in segments:
        if seg1 not in self.collapsed_segments:
          continue
        start1, end1 = seg1
        for seg2 in segments:
          if seg1 == seg2:
            continue
          if seg2 not in self.collapsed_segments:
            continue
          start2, end2 = seg2
          if end1 == start2:
            # These segments butt up against eachother
            did_something = True
            old_part1 = self.collapsed_segments[seg1]
            old_part2 = self.collapsed_segments[seg2]
            del self.collapsed_segments[seg1]
            del self.collapsed_segments[seg2]
            assert old_part1[-1] == old_part2[0]
            # Create segment with the new endpoints
            self.collapsed_segments[(start1, end2)] = old_part1[:-1] + old_part2
    for segment in list(self.collapsed_segments.keys()).copy():
      start, end = segment
      polyline = self.collapsed_segments[segment]
      # A full loop is bad for winding number, so splitting in half
      if start == end:
        split = int(len(polyline) / 2)
        self.collapsed_segments[(start, polyline[split])] = polyline[:split+1]
        self.collapsed_segments[(polyline[split], end)] = polyline[split:]
        del self.collapsed_segments[segment]

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
    for polyline in self.collapsed_segments.values():
      total += self.winding_segment(polyline, point)
    return total
  
  @functools.cache
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
  [(30,10), (40,10)],
  [(40,10), (30,20)],
  [(30,20), (40,40)],
  [(40,40), (10,40)],
  [(10,40), (10,10)],
]
  quer = WindingQuery(segments3)
  print(quer.query_winding((37,23)))

  