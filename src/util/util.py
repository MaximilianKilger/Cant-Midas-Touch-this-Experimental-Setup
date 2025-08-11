import numpy as np
import re

def polar2cartesian(point_polar, center=(0,0)):
    rho = point_polar[0]
    theta = point_polar[1]

    y= rho * np.cos(theta)
    x = rho * np.sin(theta)

    untransformed_point = np.array((x,y))
    transformed_point = untransformed_point + np.array(center)
    return transformed_point

#convert a point (x,y) from cartesian coordinates to polar coordinates
def cartesian2polar(point_cartesian, center=(0,0)):
    x = point_cartesian[0] - center[0]
    y = point_cartesian[1] - center[1]

    rho = np.sqrt(x*x+y*y)
    if x >= 0:
        theta = np.arctan(y/x)
    else:
        theta = np.arctan(y/x) + np.pi
    return rho,theta

# simple function to check if an object is iterable
def is_iterable(foo):
    try:
        bar = iter(foo)
    except:
        return False
    return True

# von Vitus
def calculate_angle(v1, v2, as_radians=False):
    angle = np.math.atan2(np.linalg.det([v1, v2]), np.dot(v1, v2))
    if as_radians:
        if angle < 0:
            angle = angle + 2 * np.pi
    else:
        angle = np.degrees(angle)
        if angle < 0:
            angle = angle + 360
    # TODO: ROUND HERE OR RETURN FLOAT INSTEAD?
    return int(angle)
# nicht mehr von Vitus

def parse_tuple_notation(string:str):
    tuple_pattern = re.compile('^\((.*,)*(.*)\)$')
    if tuple_pattern.match(string):
        string = string.strip('()')
        tup = tuple(string.split(','))
        return tup
    return None