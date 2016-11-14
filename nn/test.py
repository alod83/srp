from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler  
import matplotlib.pyplot as plt
import numpy as np
import dill

# restore training set from file
with open('training_set.pkl', 'rb') as f:
    clf = dill.load(f)
    
# current position
clng = 32.850032777778000
clat = 18.333404166667000
cspeed = 10.80
ccourse = 100.70

cstatus = [[clat,clng,ccourse,cspeed]]                   
#feature scaling
scaler = StandardScaler()
scaler.fit(cstatus)  
cstatus = scaler.transform(cstatus)  

prob = clf.predict(cstatus)

#take y list, order and remove duplicates
print prob
prob = clf.predict_proba(cstatus)
