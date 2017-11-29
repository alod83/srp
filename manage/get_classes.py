# from sklearn.externals import joblib
# import os.path
# import sys
# 
# config_path = "utilities/"
# sys.path.append(os.path.abspath(config_path))
# from config import get_training_set
# 
# 
# tp = get_training_set()
# ps = tp['prediction_steps']
# for psi in ps:
#     
#     classes = joblib.load('data/600000/classes-' + str(psi) + '.pkl') 
#     
#     out_file = open("data/600000/class-" + str(psi) + '.csv',"w")
#     for index in range(0, len(classes)):
#         out_file.write(classes[index].replace('_', ',') + '\n')
#     out_file.close()

import numpy as np
import pandas as pd
import operator
from scipy import stats, integrate

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

import seaborn as sns
sns.set(color_codes=True)

import argparse
parser = argparse.ArgumentParser(description='Train')
parser.add_argument('-n', '--number', help='number of records',required=True)
args = parser.parse_args()
nr = int(args.number)

np.random.seed(sum(map(ord, "distributions")))

import os
import sys
config_path = "/home/angelica/Git/osiris/srp/utilities/"
sys.path.append(os.path.abspath(config_path))

from MyAPI import MyAPI
from utilities import concatenate
api = MyAPI()
#X, Y = api.get_dataset(0, start_index=0,end_index=100000, nr=100000)
start_index = 1 
burst = 1000
end_index = start_index + burst
X = []
Y = []
#nr = 4051656
#nr = 430000
#nr = 7744019

while end_index <= nr:
    X_temp, Y_temp = api.get_dataset(0, start_index=start_index,end_index=end_index, nr=nr)
    if len(X_temp) > 0:
        X = concatenate(X,X_temp)
        Y = concatenate(Y,Y_temp)
    start_index = end_index + 1
    end_index = start_index + burst - 1
    if end_index > nr:
        end_index = nr
    if start_index > nr:
        end_index = nr+1

classes=list(set(Y))
Y = sorted(Y)

dist = {}
for i in range(0, len(Y)):
    try:
        dist[Y[i]] = dist[Y[i]] + 1
    except KeyError, e:
        dist[Y[i]] = 0
        dist[Y[i]] = dist[Y[i]] + 1

out_file = open("classes.csv","w")
out_file.write('row,col,value\n')
for k,v in dist.items():
    v = float(v)/nr*100
    out_file.write(k.replace('_', ',') + ',' + str(v) + '\n')
out_file.close()
#dist_y = dist.values()
#dist_x = dist.keys()