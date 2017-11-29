import numpy as np
from math import floor
from math import copysign

def get_position(x,cx,type):
    if cx > 0:
        if type == "lng":
            xg = floor(copysign((abs(x)%180),x)/cx)
            if xg == -0:
                xg = 0 
        else:
            xg = floor(x/cx)
    else:
        xg = -1
    return xg

# x/cx + x1
# get position in the grid
def get_position_in_grid(x, y, cx, cy):
    xg = get_position(x,cx,"lng")
    yg = get_position(y,cy,"lat")
    return np.array([xg, yg])

def get_points(x, cx):
    if cx > 0:
        #if type == "lng":
        #    return [float("{0:.2f}".format(x*cx)),float("{0:.2f}".format((x+1)*cx)) ]
        #else:
        return [float("{0:.2f}".format(x*cx)),float("{0:.2f}".format((x+1)*cx)) ]

def get_polygon(x,y,cx,cy):
    by = get_points(y,cy)
    bx = get_points(x,cx)
    return [[
            (bx[0],by[0]), 
            (bx[0],by[1]), 
            (bx[1],by[1]),
            (bx[1],by[0]),
            (bx[0],by[0])
        ]]
