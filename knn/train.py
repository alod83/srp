import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import dill

import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI

# Create training and test data
api = MyAPI()
X_train, Y_train = api.get_dataset('TRAINING') 
X_test, Y_test = api.get_dataset('TEST')


robust_scaler = RobustScaler()
X_train = robust_scaler.fit_transform(X_train)

# save robust scaler
with open('data/rs.pkl', 'wb') as f:
    dill.dump(robust_scaler, f)
    
X_test = robust_scaler.transform(X_test)

# Classify using k-NN
knn = KNeighborsClassifier(weights='distance',n_neighbors=3)
knn.fit(X_train, Y_train)

#save classifier 
#TODO save time
with open('data/knn.pkl', 'wb') as f:
    dill.dump(knn, f)

accuracy = knn.score(X_test, Y_test)
Y_pred = knn.predict(X_test)
  
print("\tPrecision macro: %1.3f" % precision_score(Y_test, Y_pred,average='macro'))
print("\tPrecision micro: %1.3f" % precision_score(Y_test, Y_pred,average='micro'))
print("\tPrecision weighted: %1.3f" % precision_score(Y_test, Y_pred,average='weighted'))
 
print("\tRecall macro: %1.3f" % recall_score(Y_test, Y_pred, average='macro'))
print("\tRecall micro: %1.3f" % recall_score(Y_test, Y_pred, average='micro'))
print("\tRecall weighted: %1.3f" % recall_score(Y_test, Y_pred, average='weighted'))

print("Testset accuracy using robust scaler:   %.3f" % accuracy)

