import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV

# classifiers
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import RadiusNeighborsClassifier
from sklearn.multiclass import OneVsOneClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn import tree
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.kernel_approximation import RBFSampler

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import train_test_split
import dill
from sklearn.externals import joblib
from math import sqrt
import os.path

import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI
from utilities import concatenate


# best estimator file
api = MyAPI()
ps = api.get_prediction_steps()

algorithm = "mlp"

classes = []
min_row = 349
max_row = 358
min_col = 146
max_col = 155
for row in range(min_row,max_row+1):
	for col in range(min_col,max_col+1):
		classes.append(str(row) + "_" + str(col))
#classes.append("out_of_grid")

for psi in range(0,len(ps)):
	print ps[psi]
	#start_index = 1
	#end_index = start_index + burst
	#X = []
	#Y = [] 
	X, Y = api.get_dataset(psi, table="srp_reduced",discretize=True)
    
	print(len(X))
	nr = len(X)
	n_training_per_cell = int(round(nr/(len(classes)-1)/100*80))
	n_test_per_cell = int(round(nr/(len(classes)-1)/100*20))
    
	print n_training_per_cell
	print n_test_per_cell
	
	X_train = []
	Y_train = []
	X_test = []
	Y_test = []
	index = 0
	while index < (nr - n_training_per_cell - n_test_per_cell):
		X_train = concatenate(X_train,X[index:index+n_training_per_cell])
		Y_train = concatenate(Y_train,Y[index:index+n_training_per_cell])
		X_test = concatenate(X_test,X[index+n_training_per_cell+1:index+n_training_per_cell+n_test_per_cell])
		Y_test = concatenate(Y_test,Y[index+n_training_per_cell+1:index+n_training_per_cell+n_test_per_cell])
		index = index + n_training_per_cell+n_test_per_cell + 1
	
	print len(X_train)
	print len(X_test)
    # get training
    #while end_index <= nr:
        #X_temp, Y_temp = api.get_dataset(psi, start_index=start_index,end_index=end_index, nr=nr)
        #if len(X_temp) > 0 and len(Y_temp) > 0:
        	#X = concatenate(X,X_temp)
        	#Y = concatenate(Y,Y_temp)
        
        #start_index = end_index + 1
        #end_index = start_index + burst - 1
        #if end_index > nr:
        #    end_index = nr
        #if start_index > nr:
		#    end_index = nr+1
    
	#nr_training = int(round(len(X)/100*80))
	#X_train = X[1:nr_training]
	#Y_train = Y[1:nr_training]
	
	#X_test = X[nr_training+1:len(X)]
	#Y_test = Y[nr_training+1:len(X)]
	#X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=42)
	scaler = RobustScaler()
	scaler.fit(X_train)
	X_train = scaler.transform(X_train)
	
	# store classes
	ordered_y = sorted(set(Y))
	#n_output = len(ordered_y)
	n_output = len(classes)
	#n_output = 2460
	n_input = len(X[0]) + 1
	n_neurons = int(round(sqrt(n_input*n_output)))
	print "N input" , n_input
	print "N output" , n_output
	print "N neurons", n_neurons
	classifier = MLPClassifier(solver='adam', alpha=1e-5,hidden_layer_sizes=(n_input, n_neurons, n_output), random_state=1)
	#fit_burst = burst
	#train_start = 1
	#train_stop = fit_burst
    #while train_stop <= nr_training:
    #classifier.partial_fit(X_train[train_start:train_stop], Y_train[train_start:train_stop], classes)
    #	train_start = train_stop + 1
    #	train_stop = train_start + burst - 1
    #	# 67 < 60 + 10, 
    #	if train_stop > nr_training:
    #		train_stop = nr_training
    #	if train_start >= nr_training:
    #		train_stop = nr_training + 1
	classifier.fit(X_train,Y_train)
    
    # save standard scaler
	joblib.dump(scaler, 'data/rs-' + algorithm + '-' + str(ps[psi]) + '.pkl')
    
	##save classifier
	joblib.dump(classifier, 'data/' + algorithm + '-' + str(ps[psi]) + '.pkl')
	joblib.dump(classes, 'data/classes-' + algorithm + '-' + str(ps[psi]) + '.pkl')
	
	X_test = scaler.transform(X_test)
	accuracy = classifier.score(X_test, Y_test)
	Y_pred = classifier.predict(X_test)
    
	print Y_test
	print Y_pred
          
	out_file = open("data/test-" + algorithm + '-' + str(ps[psi]) + '.txt',"w")
        
	out_file.write(str(ps[psi]) + " Precision macro: %1.3f" % precision_score(Y_test, Y_pred,average='macro') + "\n")
	out_file.write(str(ps[psi]) + " Precision micro: %1.3f" % precision_score(Y_test, Y_pred,average='micro') + "\n")
	out_file.write(str(ps[psi]) + " Precision weighted: %1.3f" % precision_score(Y_test, Y_pred,average='weighted') + "\n")
         
	out_file.write(str(ps[psi]) + " Recall macro: %1.3f" % recall_score(Y_test, Y_pred, average='macro') + "\n")
	out_file.write(str(ps[psi]) + " Recall micro: %1.3f" % recall_score(Y_test, Y_pred, average='micro') + "\n")
	out_file.write(str(ps[psi]) + " Recall weighted: %1.3f" % recall_score(Y_test, Y_pred, average='weighted') + "\n")
        
	out_file.write("Accuracy:   %.3f" % accuracy  + "\n")
	out_file.close()
        

