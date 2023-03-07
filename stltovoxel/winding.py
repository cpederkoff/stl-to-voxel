import numpy as np
import matplotlib.pyplot as plt
import math
import winding_query
x = y = np.linspace(0, 100, 100)
def normalize(num): 
  return ((num + math.pi) % (2*math.pi)) - math.pi
def winding(segments):
  total_atans = 0
  z = []
  for j in y:
    for i in x:
      total = 0
      for start, end in segments:
        start = np.array(list(start))
        end = np.array(list(end))
        # Side 1
        vec = end - start
        offset_ang = math.atan2(vec[1], vec[0])
        me = np.array([i, j])
        me_offset = me - start
        my_ang = math.atan2(me_offset[1], me_offset[0])
        ang1 = normalize(my_ang - offset_ang)
        # Side 2
        vec = start - end
        offset_ang = math.atan2(vec[1], vec[0])
        me = np.array([i, j])
        me_offset = me - end
        my_ang = math.atan2(me_offset[1], me_offset[0])
        ang2 = -1 * normalize(my_ang - offset_ang)
        total_atans += 4
        # 180 - other angles gives us angle seen by point
        total += normalize(math.pi - ang1 - ang2)
      z.append(total)
  return (np.array(z).reshape(100, 100), total_atans)

def winding_fast(segments):
  wq = winding_query.WindingQuery(segments)
  z = []
  for j in y:
    for i in x:
      z.append(wq.query_winding((i,j)))
  return np.array(z).reshape(100, 100), wq.atans


segments3 = [
        ((0, 65), (0, 32)),
        ((0, 32), (0, 31)),
        ((0, 31), (21, 6)),
        ((21, 6), (21, 5)),
        ((22, 5), (55, 0)),
        ((55, 0), (84, 16)),
        ((84, 16), (95, 48)),
        ((95, 48), (84, 79)),
        ((84, 79), (84, 80)),
        ((84, 80), (83, 80)),
        ((83, 80), (55, 97)),
    ]

segments3 =   [
  ((0.6146652, 0.3540033), (59.622562, 0.35396475)), 
  ((59.622562, 0.35396475), (30.118633, 51.3251)),
  # ((30.118633, 51.3251), (0.6146652, 0.3540033))
  ]
# segments2 = [
#   [(15,15), (15,10)],
#   # [(15,10), (15,15)],
# ]



# plt.gca().invert_yaxis()
f, axarr = plt.subplots(3,1) 
w1_img, atans1 = winding(segments3)
print(atans1)
axarr[0].imshow(w1_img, interpolation='bilinear', vmin=-math.pi, vmax=math.pi)
w2_img, atans2 = winding_fast(segments3)
print(atans2)
axarr[1].imshow(w2_img, interpolation='bilinear', vmin=-math.pi, vmax=math.pi)
# axarr[2].imshow(winding(segments3), interpolation='bilinear', vmin=-math.pi, vmax=math.pi)
plt.show()
# Test that winding is additive if you're outside 
# - Yes, outside anywhere, not just in front of.
# Test its not additive if you're inside
# - Yes, it's off by 360
# Start collapsing line segments
# Start caching collapsed line segments, and collapsing them in a good pattern