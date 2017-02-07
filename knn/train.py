import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import train_test_split
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
burst = 100
# number of records. Calculated offline for performance reasons
nr = 10000

ps = api.get_prediction_steps()
for psi in range(0,len(ps)):
    print ps[psi]
    start_index = 0
    end_index = start_index + burst
    X = []
    Y = []
    while end_index <= nr:
        print "start index: " + str(start_index) + " end index: " + str(end_index)
        #X_train_temp, Y_train_temp = api.get_dataset('true',psi, start_index=start_index,end_index=end_index) # training
        #X_test_temp, Y_test_temp = api.get_dataset('false',psi,start_index=start_index,end_index=end_index)
        #print len(X_train_temp[0])
        X_temp, Y_temp = api.get_dataset(psi, start_index=start_index,end_index=end_index)
        X = concatenate(X,X_temp)
        #print len(X_train[0])
        #print len(Y_train)
        Y = concatenate(Y,Y_temp)
        #print len(X_test)
        #print len(X_test_temp)
        #X_test = concatenate(X_test,X_test_temp)
        #print len(Y_train)
        #Y_test = concatenate(Y_test,Y_test_temp)
        
        start_index = end_index + 1
        end_index = start_index + burst - 1
        if end_index > nr:
            end_index = nr
        if start_index > nr:
            end_index = nr+1

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
    #print Y_train
    #print Y_test
    robust_scaler = RobustScaler()
    X_train = robust_scaler.fit_transform(X_train)
    
    # save robust scaler
    joblib.dump(robust_scaler, 'data/rs-' + str(ps[psi]) + '.pkl')    
    
    X_test = robust_scaler.transform(X_test)
    
    # Classify using k-NN
    knn = KNeighborsClassifier(weights='distance',n_neighbors=3)
    knn.fit(X_train, Y_train)
    
    #save classifier 
    joblib.dump(knn, 'data/knn-' + str(ps[psi]) + '.pkl')  
    
    # store classes
    ordered_y = sorted(set(Y_train))
    joblib.dump(ordered_y, 'data/classes-' + str(ps[psi]) + '.pkl')    
      
    
    accuracy = knn.score(X_test, Y_test)
    Y_pred = knn.predict(X_test)
      
    out_file = open("data/test-" + str(ps[psi]) + '.txt',"w")
    
    out_file.write(str(ps[psi]) + " Precision macro: %1.3f" % precision_score(Y_test, Y_pred,average='macro') + "\n")
    out_file.write(str(ps[psi]) + " Precision micro: %1.3f" % precision_score(Y_test, Y_pred,average='micro') + "\n")
    out_file.write(str(ps[psi]) + " Precision weighted: %1.3f" % precision_score(Y_test, Y_pred,average='weighted') + "\n")
     
    out_file.write(str(ps[psi]) + " Recall macro: %1.3f" % recall_score(Y_test, Y_pred, average='macro') + "\n")
    out_file.write(str(ps[psi]) + " Recall micro: %1.3f" % recall_score(Y_test, Y_pred, average='micro') + "\n")
    out_file.write(str(ps[psi]) + " Recall weighted: %1.3f" % recall_score(Y_test, Y_pred, average='weighted') + "\n")
    
    out_file.write("Accuracy:   %.3f" % accuracy  + "\n")
    out_file.close()
