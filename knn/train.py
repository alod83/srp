import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import dill
from sklearn.externals import joblib

import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI
from utilities import concatenate

# Create training and test data
api = MyAPI()
burst = 20000
# number of records. Calculated offline for performance reasons
nr = 500000
start_index = 0
end_index = start_index + burst
X_train = []
Y_train = []
X_test = []
Y_test = []
while end_index <= nr:
    print "start index: " + str(start_index) + " end index: " + str(end_index)
    X_train_temp, Y_train_temp = api.get_dataset('true',start_index=start_index,end_index=end_index) # training
    X_test_temp, Y_test_temp = api.get_dataset('false',start_index=start_index,end_index=end_index)
    #print len(X_train_temp[0])
    X_train = concatenate(X_train,X_train_temp)
    #print len(X_train[0])
    #print len(Y_train)
    Y_train = concatenate(Y_train,Y_train_temp)
    #print len(X_test)
    X_test = concatenate(X_test,X_test_temp)
    #print len(Y_train)
    Y_test = concatenate(Y_test,Y_test_temp)
    
    start_index = end_index + 1
    end_index = start_index + burst - 1
    if end_index > nr:
        end_index = nr
    if start_index > nr:
        end_index = nr+1


# prediction step
ps = api.get_prediction_step()

robust_scaler = RobustScaler()
X_train = robust_scaler.fit_transform(X_train)

# save robust scaler
joblib.dump(robust_scaler, 'data/rs-' + str(ps) + '.pkl')    

X_test = robust_scaler.transform(X_test)

# Classify using k-NN
knn = KNeighborsClassifier(weights='distance',n_neighbors=3)
knn.fit(X_train, Y_train)

#save classifier 
joblib.dump(knn, 'data/knn-' + str(ps) + '.pkl')  

# store classes
ordered_y = sorted(set(Y_train))
joblib.dump(ordered_y, 'data/classes-' + str(ps) + '.pkl')    
  

accuracy = knn.score(X_test, Y_test)
Y_pred = knn.predict(X_test)
  
print("\tPrecision macro: %1.3f" % precision_score(Y_test, Y_pred,average='macro'))
print("\tPrecision micro: %1.3f" % precision_score(Y_test, Y_pred,average='micro'))
print("\tPrecision weighted: %1.3f" % precision_score(Y_test, Y_pred,average='weighted'))
 
print("\tRecall macro: %1.3f" % recall_score(Y_test, Y_pred, average='macro'))
print("\tRecall micro: %1.3f" % recall_score(Y_test, Y_pred, average='micro'))
print("\tRecall weighted: %1.3f" % recall_score(Y_test, Y_pred, average='weighted'))

print("Testset accuracy using robust scaler:   %.3f" % accuracy)

