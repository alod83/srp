# fare tanti training set temporale : 15 min, 30 min, 1h
# training set spaziale: 0.01x0.01 ...
# tra le features considerare anche le traiettorie precedenti

from sklearn.neural_network import MLPClassifier
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# features : current row, col
# take a route, order by timestamp ASC
# for each status, take the next status as the following
import os
import sys
from __builtin__ import True

from geo import get_position_in_grid
from config import get_grid
gp = get_grid()

from conn import MyConn

def check_ts(t1,t2,step):
    if t1 == t2:
        return False
    timedelta = t1 - t2
    min = timedelta.seconds/60
    
    if min >= step and min <= 2*step:
        return True
    return False
    

SQLObj = MyConn()
X = []
y = []
ships = SQLObj.get_all_from_locality()
for rows in ships:
    n = len(rows)
    for i in range(0, n-1):
        #print i
        # cx , cy must contain latitude and longitude
        #[cx, cy] = get_position_in_grid(float(rows[i]['LONGITUDE']), float(rows[i]['LATITUDE']), float(gp['cx']), float(gp['cy']))
        # next status is the one after 15 minutes
        # if there is not a next status, calculate interpolation
        
        # search the next hop
        
        #nrow = [x for x in rows[i+1:n] if check_ts(x['TIMESTAMP'],rows[i]['TIMESTAMP'])]
        nlat = None
        nlng = None
        # take the first available position as next
        for ns in rows[i+1:n]:
           if check_ts(ns['TIMESTAMP'],rows[i]['TIMESTAMP'],SQLObj.get_prediction_step()):
                nlat = float(ns['LATITUDE'])
                nlng = float(ns['LONGITUDE'])
                nts = ns['TIMESTAMP']
                break
        # if not found, manage
        if nlat is None:
            continue
            
        #print rows[i]['TIMESTAMP']
        #print nts
        
        [nx,ny] = get_position_in_grid(nlng, nlat, float(gp['cx']), float(gp['cy']))
        # consider also speed, course, timestamp
        features = [
            float(rows[i]['LATITUDE']),
            float(rows[i]['LONGITUDE']),
            float(rows[i]['COURSE']),
            float(rows[i]['SPEED'])
        ]
        X.append(features)
        y.append(str(ny) + "_" + str(nx))
        
    # TODO last row
#     [cx, cy] = get_position_in_grid(float(rows[n-1]['LONGITUDE']), float(rows[n-1]['LATITUDE']), float(gp['cx']), float(gp['cy']))
#     features = [
#         float(rows[n-1]['LATITUDE']),
#         float(rows[n-1]['LONGITUDE']),
#         float(rows[n-1]['COURSE']),
#         float(rows[n-1]['SPEED'])
#     ]
#     X.append(features)
#     y.append('exit')
    
#take y list, order and remove duplicates
ordered_y = sorted(set(y))
   
clf = MLPClassifier(solver='lbfgs', alpha=1e-5, random_state=1, verbose=True)
clf.fit(X, y)   

# current position
clng = 35.850032777778000
clat = 11.333404166667000
cspeed = 1.80
ccourse = 20.70
cstatus = [[clat,clng,ccourse,cspeed]]                    

prob = clf.predict_proba(cstatus).tolist()

print prob

result = {}
for i in range(0,len(ordered_y)):
    result[ordered_y[i]] = prob[0][i]

#print result
#print sorted(result.items(), key=result.get, reverse=True)

cx,cy = get_position_in_grid(clng, clat, float(gp['cx']), float(gp['cy']))

cx = int(cx)
cy = int(cy)
print str(cx) + " " + str(cy)
print clf.predict(cstatus)
   
 
#here's our data to plot, all normal Python lists
   
# retrieve rows and columns from array of output
x = []
y  = []
for i in range(0,len(ordered_y)-1):
    [c,r] = ordered_y[i].split("_")
    r = float(r)
    c = float(c)
    if c not in x:
        x.append(c)
    if r not in y:
        y.append(r)
x =  sorted(x)
y = sorted(y)

intensity = [0] * len(y)
for i in range(0, len(intensity)):
    intensity[i] = [0] * len(x)
 
min_x = int(x[0]) 
min_y = int(y[0]) 
 
for r in y:
    for c in x:
        key = str(c) + "_" + str(r)
        try:
            # current row (cr) and current column (cc) represent the index of the matrix
            # they are calculated as the difference between the current value and the minimum
            cr = int(r)-int(min_y)
            cc = int(c)-int(min_x)
            intensity[cr][cc] = float(result[key])
        except KeyError:
            continue
        except TypeError:
            continue
# set the intensity of current position to 1
#setup the 2D grid with Numpy
x, y = np.meshgrid(x, y)

intensity[cy-min_y][cx-min_x] = 1
#convert intensity (list of lists) to a numpy array for plotting
intensity = np.array(intensity)

#now just plug the data into pcolormesh, it's that easy!
plt.pcolormesh(x, y, intensity)
plt.colorbar() #need a colorbar to show the intensity scale
plt.show() #boom 