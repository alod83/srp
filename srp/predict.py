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
config_path = "/home/angelica/Git/osiris/srp/utilities/"
sys.path.append(os.path.abspath(config_path))

from geo import get_position_in_grid
from geo import get_polygon
from config import get_grid
from config import get_training_set
from MyAPI import MyAPI
from utilities import print_result
from numpy.distutils.misc_util import cxx_ext_match
import json

import argparse
import time
from datetime import datetime

def platt_func(x):
    return 1/(1+np.exp(-x))
    
def parse_recordid(args,discretize):
	record_id = args.record_id
	# TODO correggere psi: 0,1,2 in modo da avere la predizione a 30, 45 e 60
	
	tp = get_training_set()
	psl = tp['prediction_steps']
	api = MyAPI()
	X = []
	y = {} 
	for psi in range(0,len(psl)):
		ps = str(psl[psi])
		# X is always the same, y is not
		X_temp,y_temp = api.get_dataset(psi,record_id=record_id,nr=1,discretize=discretize)
		if len(X_temp) > 0:
			X = X_temp
		if len(y_temp) > 0:
			y[ps] = y_temp.tolist()
	return X,y
	
def parse_features(args,discretize):
	
	gp = get_grid()

	clat = float(args.latitude)
	clng = float(args.longitude)
	[x,y] = get_position_in_grid(clng, clat, float(gp['cx']),float(gp['cy']))
	cspeed = float(args.speed)
	
	ccourse = float(args.course)
	ccourse_sin = math.sin(float(args.course))
	ccourse_cos = math.cos(float(args.course))
	bc = int(args.basic_class)
	#cstatus_orig = [[int(y),int(x),ccourse_sin,ccourse_cos,cspeed, bc]] 
	cstatus_orig = [[clat,clng,ccourse_sin,ccourse_cos,cspeed, bc]] 
	
	if discretize:
		dspeed = api.get_discretized_speed(cspeed)
		dcourse = api.get_discretized_course(ccourse)
		cstatus_orig = [[int(y),int(x),dspeed,dcourse, bc]]
	return cstatus_orig,None

# receive the current position, the speed, the course and time as input

parser = argparse.ArgumentParser(description='Ship Route Preditction')
subparsers = parser.add_subparsers()

recordid_p = subparsers.add_parser('record_id')
recordid_p.add_argument('-r', '--record_id', help='define record_id',required=True)
recordid_p.set_defaults(func=parse_recordid)

features_p = subparsers.add_parser('features')
features_p.add_argument('-l', '--latitude', help='define current latitude',type=float,required=True)
features_p.add_argument('-n', '--longitude', help='define current longitude',type=float,required=True)
features_p.add_argument('-s', '--speed',help='define current speed',required=True)
features_p.add_argument('-c', '--course',help='define current course',required=True)
features_p.add_argument('-b', '--basic_class',help='define basic class (0 = small ship, 1 = medium ship, 2 = big ship)',required=True)
features_p.set_defaults(func=parse_features)

parser.add_argument('-a', '--algorithm',help='select algorithm (default knn (knn, one-vs-one, one-vs-rest,gaussian-nb,bernoulli-nb,decision-tree,svm,linear-svm,mlp,radius-neighbor,sgd,kernel-approx)',required=False)
parser.add_argument('-i', '--sdi',help='ship identifier',required=False)
parser.add_argument('-f', '--no_feature_collection',action='store_true',help='set output without feature collection',required=False)
parser.add_argument('-d', '--discretize',action='store_true',help='set feature discretization',required=False)
parser.add_argument('-v', '--verbose',action='store_true',help='set verbosity',required=False)

parser.add_argument('-o', '--output',help='specify output file name',required=False)

args = parser.parse_args()

startTime = datetime.now()

algorithm = "knn"
if args.algorithm is not None:
    algorithm = args.algorithm
    
verbose = False
if args.verbose:
    verbose = True;
    
sdi = None
if args.sdi is not None:
    sdi = args.sdi

no_feature_collection = False
if args.no_feature_collection:
    no_feature_collection = True
    
discretize = False
if args.discretize:
	discretize = True
	
# current position
cstatus_orig,y = args.func(args,discretize)
	
api = MyAPI()
# prediction step
# TODO manage prediction step
#ps = args.prediction_steps

#print cstatus_orig

prop = {}
polygons = {}
tp = get_training_set()
gp = get_grid()
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
                if sdi is not None:
                	prop[classes[i]]['sdi'] = sdi
            	prop[classes[i]]['type'] = "probability"
i=0           
for key in prop:
	pol = Polygon(polygons[key])
	if no_feature_collection is True:
		result = dumps({'type': 'Feature', 'geometry' : pol, "properties" : prop[key]})
		print_result(args.output,result)
		if i < len(prop)-1:
			print_result(args.output,",")
	else:
		features.append(Feature(geometry=pol,properties=prop[key]))
	i = i + 1
	
if y is not None and no_feature_collection is False:
	prop = {}
	polygon = {}
	for ps in psl:
		ps = str(ps)
		
		if ps in y:
			coord = y[ps][0].split("_")
			label = y[ps][0]
			polygon[label] = get_polygon(int(coord[1]),int(coord[0]),float(gp['cx']),float(gp['cy']))
			try:
				
				prop[label]['row'] = int(coord[0])
				prop[label]['column'] = int(coord[1])
				prop[label]['type'] = "effective"
				prop[label]['delta'].append(ps)
			except KeyError:
				prop[label] = {}
				prop[label]['row'] = int(coord[0])
				prop[label]['column'] = int(coord[1])
				prop[label]['type'] = "effective"
				prop[label]['delta'] = [ps]
	for key in prop:			
		pol = Polygon(polygon[key])
		myprop = prop[key]
		features.append(Feature(geometry=pol,properties=myprop))
	
if no_feature_collection is False:
	result = FeatureCollection(features)
	result = dumps(result)
	print_result(args.output,result)

if verbose:
	seconds = datetime.now() - startTime
	print "Number of seconds to execute the script: " + str(seconds)
