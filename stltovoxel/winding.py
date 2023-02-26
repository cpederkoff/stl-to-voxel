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
  [(10,10), (20,10)],
  [(20,10), (30,10)],
  [(30,10), (40,10)],
  [(40,10), (30,20)],
  [(30,20), (40,40)],
  [(40,40), (10,40)],
  [(10,40), (10,10)],
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