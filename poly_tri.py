# poly_tri.py PyPolygon2tri 1.0, triangulation by ear cutting algorithm.
# Copyright (C) 2007 Sebastian Santisi <s@ntisi.com.ar>
# Copyright (C) 1988 Evans & Sutherland Computer Corporation
"""
This version is a Python ported version from C by Sebastian Santisi.
C version available at
http://www.programmersheaven.com/download/15162/download.aspx

I've ported this algorithm because GLU Tesselator (gluTess* functions)
throws a stack overflow exception for Python in Windows.


C preamble:
/*
 * poly_tri.c
 *
 * Program to take a polygon definition and convert it into triangles
 * that may then be rendered by the standard triangle rendering
 * algorithms.  This assumes all transformations have been performed
 * already and cuts them up into optimal triangles based on their
 * screen-space representation.
 *
 *	Copyright (c) 1988, Evans & Sutherland Computer Corporation
 *
 * Permission to use all or part of this program without fee is
 * granted provided that it is not used or distributed for direct
 * commercial gain, the above copyright notice appears, and
 * notice is given that use is by permission of Evans & Sutherland
 * Computer Corporation.
 *
 *	Written by Reid Judd and Scott R. Nelson at
 *	Evans & Sutherland Computer Corporation (January, 1988)
 *
 * To use this program, either write your own "draw_triangle" routine
 * that can draw triangles from the definitions below, or modify the
 * code to call your own triangle or polygon rendering code.  Call
 * "draw_poly" from your main program.
 */
"""

COUNTER_CLOCKWISE = 0
CLOCKWISE = 1

def orientation(v):
	"""
	Return either clockwise or counter_clockwise for the orientation
	of the polygon.
	"""

	area = 0.0
     	# Compute the area (times 2) of the polygon
	for i in range(len(v)):
		area += v[i-1][0]*v[i][1] - v[i-1][1]*v[i][0]

	if area >= 0.0:
		return COUNTER_CLOCKWISE
	return CLOCKWISE

def determinant(p1, p2, p3):
	"""
	Computes the determinant of the three points.
	Returns whether the triangle is clockwise or counter-clockwise.
	"""

	determ = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])

	if determ >= 0:
		return CLOCKWISE
	return COUNTER_CLOCKWISE

def no_interior(p1, p2, p3, v, poly_or):
	"""
	Returns 1 if no other point in the vertex list is inside
	the triangle specified by the three points.  Returns
	0 otherwise.
	"""

	for p in v:
		if p == p1 or p == p2 or p == p3:
			# Don't bother checking against yourself
			continue
		if determinant(p1, p2, p) == poly_or or \
			determinant(p3, p1, p) == poly_or or \
			determinant(p2, p3, p) == poly_or:
				# This point is outside
				continue
		# The point is inside
		return False
	# No points inside this triangle
	return True

def draw_triangle(p1, p2, p3, *args):
	"""
	Rewrite this function, or pass a callback to draw_poly().
	"""
	pass

def draw_poly(v, callback=draw_triangle, args=None, poly_orientation=None):
	"""
	Call this procedure with a polygon, this divides it into triangles
	and calls the triangle routine once for each triangle.

	Note that this does not work for polygons with holes or self
	penetrations.
	"""

	if poly_orientation == None:
		poly_orientation = orientation(v)

	v = v[:]
	# Pop clean triangles until nothing remains
	while len(v) > 3:
		for cur in range(len(v)):
			prev = cur - 1
			next = (cur + 1) % len(v) # Wrap around on the ends
				# By definition, at least there are two ears;
				# we will iterate at end only if poly_orientation
				# was incorrect.
			if determinant(v[cur], v[prev], v[next]) == poly_orientation and \
				no_interior(v[prev], v[cur], v[next], v, poly_orientation):
				# Same orientation as polygon
				# No points inside
					# Output this triangle
					callback(v[prev], v[cur], v[next], args)
					# Remove the triangle from the polygon
					del(v[cur])
					break
		else:
			raise('Error: Didn\'t find a triangle.\n')

	# Output the final triangle
	callback(v[0], v[1], v[2], args)
