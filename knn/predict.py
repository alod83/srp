#!/usr/bin/python

# This script predicts the grid of probabilities
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import json
import math
from sklearn.externals import joblib

import os
import sys
from scipy.odr.odrpack import Output
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))

from geo import get_position_in_grid
from config import get_grid
from MyAPI import MyAPI
from numpy.distutils.misc_util import cxx_ext_match
import json

import argparse
import time

# receive the current position, the speed, the course and time as input

parser = argparse.ArgumentParser(description='Ship Route Preditction')
parser.add_argument('-l', '--latitude', help='define current latitude',type=float,required=True)
parser.add_argument('-n', '--longitude', help='define current longitude',type=float,required=True)
parser.add_argument('-s', '--speed',help='define current speed',required=True)
parser.add_argument('-c', '--course',help='define current course',required=True)
parser.add_argument('-b', '--basic_class',help='define basic class (0 = small ship, 1 = medium ship, 2 = big ship)',required=True)
parser.add_argument('-p', '--prediction_step',help='define prediction step',required=True)

parser.add_argument('-o', '--output',help='specify output file name',required=False)

args = parser.parse_args()
    
api = MyAPI()
# prediction step
# TODO manage prediction step
ps = args.prediction_step
gp = get_grid()

# restore classifier set from file
knn = joblib.load('data/knn-' + ps + '.pkl') 

# restore robust scaler from file
robust_scaler = joblib.load('data/rs-' + ps + '.pkl') 

# restore classes from file
classes = joblib.load('data/classes-' + ps + '.pkl') 

# current position
clat = float(args.latitude)
clng = float(args.longitude)
cspeed = float(args.speed)
ccourse_sin = math.sin(float(args.course))
ccourse_cos = math.cos(float(args.course))
bc = int(args.basic_class)
cstatus = [[clat,clng,ccourse_sin,ccourse_cos,cspeed, bc]]                    
cstatus = robust_scaler.transform(cstatus)

prob = knn.predict_proba(cstatus).tolist()

result = {}
for i in range(0,len(classes)):
    result[classes[i]] = float("{0:.2f}".format(prob[0][i]))

#print json.dumps(prob)

#sys.stdout.write(json.dumps(prob))
#sys.stdout.flush()

result = json.dumps(result)
if args.output is None:
    print result
else:
    with open(args.output, 'wb') as fh:
        fh.write(result)
