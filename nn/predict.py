# This script predicts the grid of probabilities
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
import numpy as np
import dill

import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))

from geo import get_position_in_grid
from config import get_grid
from MyAPI import MyAPI
from numpy.distutils.misc_util import cxx_ext_match
import json

import argparse

# receive the current position, the speed, the course and time as input

parser = argparse.ArgumentParser(description='Ship Route Preditction')
parser.add_argument('-l', '--latitude', help='define current latitude',type=float,required=True)
parser.add_argument('-n', '--longitude', help='define current longitude',type=float,required=True)
parser.add_argument('-s', '--speed',help='define current speed',required=True)
parser.add_argument('-c', '--course',help='define current course',required=True)
args = parser.parse_args()

api = MyAPI()
gp = get_grid()

# restore classifier set from file
with open('data/knn.pkl', 'rb') as f:
    knn = dill.load(f)

# restore robust scaler set from file
with open('data/rs.pkl', 'rb') as f:
    robust_scaler = dill.load(f)

X_train,y_train = api.get_dataset('TRAINING') 
ordered_y = sorted(set(y_train))

# current position
# current position
clat = float(args.latitude)
clng = float(args.longitude)
cspeed = float(args.speed)
ccourse = float(args.course)
cstatus = [[clat,clng,ccourse,cspeed]]                    
cstatus = robust_scaler.transform(cstatus)

#next_lng = 34.800168333333000
#next_lat = 13.33338111111100

print knn.predict(cstatus)

#nx,ny = get_position_in_grid(next_lng, next_lat, float(gp['cx']), float(gp['cy']))
#print str(nx) + "_" + str(ny)
                  
#cstatus = robust_scaler.transform(cstatus)

prob = knn.predict_proba(cstatus).tolist()

#print knn.predict(cstatus)

result = {}
for i in range(0,len(ordered_y)):
    result[ordered_y[i]] = prob[0][i]

result = {}
for i in range(0,len(ordered_y)):
    result[ordered_y[i]] = prob[0][i]
 
#print json.dumps(result)
#print sorted(result.items(), key=result.get, reverse=True)
# 
cx,cy = get_position_in_grid(clng, clat, float(gp['cx']), float(gp['cy']))
# 
cx = int(cx)
cy = int(cy)

x = []
y  = []
for i in range(0,len(ordered_y)):
    [c,r] = ordered_y[i].split("_")
    r = float(r)
    c = float(c)
    if c not in x:
        x.append(c)
    if r not in y:
        y.append(r)
x = sorted(x)
y = sorted(y)
 
# add missing values
min_x = int(x[0]) 
min_y = int(y[0]) 
 
max_x = int(max(x)) 
max_y = int(min(x)) 
 
complete_x = list(range(min_x,max_x+1))
complete_y = list(range(min_y,max_y+1))
  
intensity = [0] * len(complete_y)
 
for i in range(0, len(intensity)):
    intensity[i] = [0] * len(complete_x)
 
 
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
complete_x, complete_y = np.meshgrid(complete_x, complete_y)
  
intensity[cx-min_y][cy-min_x] = 1
#convert intensity (list of lists) to a numpy array for plotting
intensity = np.array(intensity)
  
#now just plug the data into pcolormesh, it's that easy!
pc = plt.pcolormesh(complete_x, complete_y, intensity,cmap='ocean_r')
 
plt.colorbar() #need a colorbar to show the intensity scale
plt.grid()
plt.show() #boom 