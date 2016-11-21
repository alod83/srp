from MyAPI import MyAPI
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler 
from sklearn.metrics import precision_recall_fscore_support 
import matplotlib.pyplot as plt
import numpy as np
import dill

# restore training set from file
with open('training_set.pkl', 'rb') as f:
    clf = dill.load(f)
    
# restore label matrix
with open('labels.pkl', 'rb') as f:
    le = dill.load(f)
    
# get all the elements in the testset
api = MyAPI()
X,y = api.get_dataset('TEST') 
# for each element in the testset predict the next position
y_pred = []
for i in range(0,len(X)):
    #feature scaling
    scaler = MinMaxScaler(feature_range=(-1, 1))
    #scaler.fit(X[i])  
    cstatus = scaler.transform(X[i])  
    y_pred.append(clf.predict([cstatus]))
    
le.transform(y)
print precision_recall_fscore_support(y, y_pred)

    
# calculate precision, recall f-measure, accuracy
# current position
                 
    

#take y list, order and remove duplicates
#print prob
#prob = clf.predict_proba(cstatus)
