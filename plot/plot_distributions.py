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

np.random.seed(sum(map(ord, "distributions")))

import os
import sys
config_path = "utilities/"
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
nr = 4051656
#nr = 10000
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

le = LabelEncoder()
le.fit(classes)
Y = le.transform(Y)


dist = {}
for i in range(0, len(Y)):
    try:
        dist[Y[i]] = dist[Y[i]] + 1
    except KeyError, e:
        dist[Y[i]] = 0
        dist[Y[i]] = dist[Y[i]] + 1

dist_y = dist.values()
dist_x = dist.keys()

#print dist_y
#print dist_x
plt.clf()
plt.xlabel('Classes')
plt.ylabel('Number of records')
plt.title('Number of records VS Classes')
#plt.yscale('log')
plt.plot(dist_x, dist_y)
plt.savefig('dist-log.png')
#le = LabelEncoder()
#le.fit(classes)
#x = np.random.normal(size=100)
#Y = le.transform(Y)
#my_plot = sns.distplot(Y);
#print Y
print len(classes)
#print sorted(Y)

#fig = my_plot.get_figure()
#fig.savefig("distribution.png") 
