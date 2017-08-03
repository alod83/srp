#!/usr/bin/python

# This script predicts the grid of probabilities
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.kernel_approximation import RBFSampler
import numpy as np
import json
import math
from sklearn.externals import joblib
from geojson import Feature, Polygon, FeatureCollection, dumps

import os
import sys
from scipy.odr.odrpack import Output
from matplotlib.backends.backend_ps import ps_backend_helper
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))

from geo import get_position_in_grid
from geo import get_polygon
from config import get_grid
from config import get_training_set
from MyAPI import MyAPI
from numpy.distutils.misc_util import cxx_ext_match
import json

import argparse
import time

def platt_func(x):
    return 1/(1+np.exp(-x))

# receive the current position, the speed, the course and time as input

parser = argparse.ArgumentParser(description='Ship Route Preditction')
parser.add_argument('-l', '--latitude', help='define current latitude',type=float,required=True)
parser.add_argument('-n', '--longitude', help='define current longitude',type=float,required=True)
parser.add_argument('-s', '--speed',help='define current speed',required=True)
parser.add_argument('-c', '--heading',help='define current heading',required=True)
parser.add_argument('-b', '--basic_class',help='define basic class (0 = small ship, 1 = medium ship, 2 = big ship)',required=True)
parser.add_argument('-a', '--algorithm',help='select algorithm (default knn (knn, one-vs-one, one-vs-rest,gaussian-nb,bernoulli-nb,decision-tree,svm,linear-svm,mlp,radius-neighbor,sgd,kernel-approx)',required=False)

parser.add_argument('-o', '--output',help='specify output file name',required=False)

args = parser.parse_args()

algorithm = "knn"
if args.algorithm is not None:
    algorithm = args.algorithm

    
api = MyAPI()
# prediction step
# TODO manage prediction step
#ps = args.prediction_steps
tp = get_training_set()

gp = get_grid()

# current position
clat = float(args.latitude)
clng = float(args.longitude)
[x,y] = get_position_in_grid(clng, clat, float(gp['cx']),float(gp['cy']))
cspeed = float(args.speed)
#if args.heading == '0':
    
cheading = float(args.heading)
cheading_sin = math.sin(float(args.heading))
cheading_cos = math.cos(float(args.heading))
bc = int(args.basic_class)
#cstatus_orig = [[int(y),int(x),cheading_sin,cheading_cos,cspeed, bc]] 
cstatus_orig = [[clat,clng,cheading_sin,cheading_cos,cspeed, bc]] 
#cstatus = [[int(y),int(x),cheading,cspeed, bc]] 

#print cstatus

prop = {}
polygons = {}
psl = tp['prediction_steps']
features = []
for ps in psl:
    
    ps = str(ps)
    
    #prop['probability_' + ps] = []
    #prop['class_' + ps] = []
    # restore classifier set from file
    classifier = joblib.load('data/' + algorithm + '-' + ps + '.pkl') 
    
    # restore robust scaler from file
    robust_scaler = joblib.load('data/rs-' + algorithm + '-' + ps + '.pkl') 
    
    # restore classes from file
    classes = joblib.load('data/classes-' + algorithm + '-' + ps + '.pkl') 
    
    
    cstatus = robust_scaler.transform(cstatus_orig)
    
    if algorithm == 'kernel-approx':
        rbf_feature = RBFSampler(gamma=1, random_state=1)
        cstatus = rbf_feature.fit_transform(cstatus)
        
    prob = None
    if algorithm == 'one-vs-rest' or algorithm == 'linear-svm':
        f = np.vectorize(platt_func)
        raw_predictions = classifier.decision_function(cstatus)
        platt_predictions = f(raw_predictions)
        prob = platt_predictions / platt_predictions.sum(axis=1)
        #prob = prob.tolist()
        
    else:
        prob = classifier.predict_proba(cstatus).tolist()
        
    
    for i in range(0,len(classes)):
        
        if algorithm == 'one-vs-rest'  or algorithm == 'linear-svm':
            nz_prob = float("{0:.4f}".format(prob[0][i]))
        else:
            nz_prob = float("{0:.2f}".format(prob[0][i]))
        if nz_prob > 0:
            coord = classes[i].split("_")
            #print coord
            polygons[classes[i]] = get_polygon(int(coord[1]),int(coord[0]),float(gp['cx']),float(gp['cy']))
           
            try:
               prop[classes[i]]['probability_' + ps] = nz_prob
               prop[classes[i]]['row'] = int(coord[0])
               prop[classes[i]]['column'] = int(coord[1])
            except KeyError:
                prop[classes[i]] = {}
                prop[classes[i]]['probability_' + ps] = nz_prob
                prop[classes[i]]['row'] = int(coord[0])
                prop[classes[i]]['column'] = int(coord[1])
            
            
for key in prop:
    # TO DO build polygon
    #pol = Polygon([[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.38, 57.322)]])
    pol = Polygon(polygons[key])
    features.append(Feature(geometry=pol,properties=prop[key]))
# build the output in geojson
#result = {}
#for i in range(0,len(classes)):
#    result[classes[i]] = float("{0:.2f}".format(prob[0][i]))
  
#print json.dumps(prob)
result = FeatureCollection(features)
#sys.stdout.write(json.dumps(prob))
#sys.stdout.flush()

result = dumps(result)
if args.output is None:
    print result
else:
    with open(args.output, 'wb') as fh:
        fh.write(result)

#print knn.predict(cstatus)
#pos = get_position_in_grid(clng,clat,0.1,0.1)
#print get_polygon(pos[0], pos[1], 0.1,0.1)
