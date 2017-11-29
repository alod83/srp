import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import StandardScaler
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

base_path = "/home/angelica/Git/osiris/srp/"
import os
import sys
config_path = base_path + "utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI
from utilities import concatenate

import argparse

parser = argparse.ArgumentParser(description='Train')
parser.add_argument('-a', '--algorithm', help='algorithm (knn, one-vs-one, one-vs-rest,gaussian-nb,bernoulli-nb,decision-tree,svm,linear-svm,mlp,radius-neighbor,sgd,kernel-approx)',required=False)
parser.add_argument('-n', '--number', help='number of records',required=True)
parser.add_argument('-b', '--burst', help='burst size',required=False)
parser.add_argument('-c', '--cross_validation', action='store_true',help='enable cross validation',required=False)
parser.add_argument('-p', '--partial_fit',action='store_true',help='enable partial fit',required=False)
parser.add_argument('-t', '--test_set_size',help='test_set_size',required=False)

args = parser.parse_args()

algorithm = "knn"
if args.algorithm is not None:
    algorithm = args.algorithm

# cross validation
cv = False
if args.cross_validation:
    cv = True
    
# partial fit
pf = False
if args.partial_fit:
	pf = True

burst = 100
if args.burst:
	int(args.burst)
	
nr_test = 250000
if args.test_set_size:
	nr_test = int(args.test_set_size)
	
nr = int(args.number)

classifier = None
parameters = None
# best estimator file
api = MyAPI()
exists_be_file = None
ps = api.get_prediction_steps()
# check whether the cross validation was already run
be_file_bu = base_path + 'data/best-estimator-' + algorithm + '-'
be_file = be_file_bu + str(ps[0]) + ".pkl"
exists_be_file = os.path.exists(be_file)

cv_classifier = []
if exists_be_file is True and cv is False:
    for psi in range(0,len(ps)):
        cv_classifier.append(joblib.load(be_file_bu + str(ps[psi]) + ".pkl"))
    print "exists_be_file " + str(exists_be_file)
elif algorithm == 'knn':
    classifier = KNeighborsClassifier(weights='distance',n_neighbors=5)
    if cv:
        parameters = {  'n_neighbors'   : np.arange(3, 8),
                        'weights'       : ['uniform', 'distance'],
                        'metric'        : ['euclidean', 'manhattan', 'chebyshev', 'minkowski'],
                        'algorithm'     : ['auto', 'ball_tree', 'kd_tree'],
                       # 'leaf_size'     : np.arange(30,50)
                    }
elif algorithm == 'one-vs-one':
    classifier = OneVsOneClassifier(LinearSVC(random_state=0))
    if cv:
        parameters = {  'estimator'   : [LinearSVC(random_state=0), svm.LinearSVC()]}
elif algorithm == 'one-vs-rest':
    classifier = OneVsRestClassifier(LinearSVC(random_state=0)) 
    if cv:
        parameters = {  'estimator'   : [LinearSVC(random_state=0), svm.LinearSVC()]}
# gaussian naive bayes
elif algorithm == 'gaussian-nb':
    classifier = GaussianNB()  
    if cv:
        parameters = {}
# bernoulli naive bayes
elif algorithm == 'bernoulli-nb':
    classifier = BernoulliNB()
    if cv:
        parameters = {  'alpha'       : 0.1 * np.arange(0, 10)}
elif algorithm == 'decision-tree':
    classifier = tree.DecisionTreeClassifier()
    if cv:
        parameters = {  'criterion'   : ['gini', 'entropy'],
                        'splitter'    : ['best', 'random']
                    }
elif algorithm == 'svm':
    classifier = svm.SVC(decision_function_shape='ovo')
    if cv:
        parameters = {  'kernel'                    : [ 'poly', 'rbf', 'sigmoid'],
                        'decision_function_shape'   : ['ovo', 'ovr', 'None']
                    }
elif algorithm == 'linear-svm':
    classifier = svm.LinearSVC()
    if cv:
        parameters = {  'loss'      : ['hinge', 'squared_hinge']}
elif algorithm == 'mlp':
    #classifier = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5, 2), random_state=1)
    if cv:
        parameters = {'alpha'   : [1e-5], 
                      'solver'          : ['lbfgs', 'sgd', 'adam'],
                      'activation'      : ['identity', 'logistic', 'tanh', 'relu'],
                      'learning_rate'   : ['constant', 'invscaling', 'adaptive']
                }
elif algorithm == 'radius-neighbor':
    classifier = RadiusNeighborsClassifier(radius=100.0)  
    if cv:
        parameters = { 'weights'         : ['uniform', 'distance'],
                       'algorithm'       : ['auto', 'ball_tree', 'kd_tree', 'brute']
        }     
elif algorithm == 'sgd' or algorithm == 'kernel-approx':
    classifier = SGDClassifier(loss="hinge", penalty="l2")
    if cv:
        parameters = { 'loss'           : ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
                       'penalty'        : ['none', 'l2', 'l1', 'elasticnet'],
                      'alpha'           : 10.0 ** -np.arange(1, 5)
                      #'learning_rate'   : ['constant', 'optimal', 'invscaling']
        }
    

for psi in range(0,len(ps)):
    print ps[psi]
    start_index = 1 
    end_index = start_index + burst
    X = []
    Y = []
    robust_scaler = RobustScaler()
    
    while end_index <= nr:
        X_temp, Y_temp = api.get_dataset(psi, start_index=start_index,end_index=end_index, nr=nr)
        if len(X_temp) > 0:
            X = concatenate(X,X_temp)
            Y = concatenate(Y,Y_temp)
            
        start_index = end_index + 1
        end_index = start_index + burst - 1
        if end_index > nr:
            end_index = nr
        if start_index > nr:
            end_index = nr+1

	test_size = 0.20
	if pf is True:
		test_size = 0.05
    #X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size, random_state=42)
    
    X_test = X[0:nr_test]
    Y_test = Y[0:nr_test]
    X_train = X[nr_test+1:len(X)]
    Y_train = Y[nr_test+1:len(X)]
     
    X_train = robust_scaler.fit_transform(X_train)
    
    # save standard scaler
    joblib.dump(robust_scaler, base_path + 'data/rs-' + algorithm + '-' + str(ps[psi]) + '.pkl')    
    
    X_test = robust_scaler.transform(X_test)
    
    if algorithm == 'kernel-approx':
        rbf_feature = RBFSampler(gamma=1, random_state=1)
        X_train = rbf_feature.fit_transform(X_train)
        X_test = rbf_feature.fit_transform(X_test)
    elif algorithm == 'mlp':
    	n_output = len(set(Y))
    	#n_output = 2460
    	n_input = len(X_train[0]) + 1
    	n_neurons = int(round(sqrt(n_input*n_output)))
    	print "N input" , n_input
    	print "N output" , n_output
    	print "N neurons", n_neurons
    	classifier = MLPClassifier(solver='adam', alpha=1e-5,hidden_layer_sizes=(n_input, n_neurons, n_output), random_state=1)
        
    if classifier is not None or exists_be_file is True:
        
        if cv is True:
            gs = GridSearchCV(classifier, parameters)
            gs.fit(X_train, Y_train)
            classifier = gs.best_estimator_
            print(gs.best_estimator_)
            # save best estimator
            joblib.dump(gs.best_estimator_, base_path + 'data/best-estimator-' + algorithm + '-' + str(ps[psi]) + '.pkl')   
        elif exists_be_file is True:
            classifier = cv_classifier[psi]
        
        if pf is True:
        	classes = []
        	min_row = 323
        	max_row = 377
        	min_col = 99
        	max_col = 160
        	for row in range(min_row,max_row+1):
        		for col in range(min_col,max_col+1):
        			classes.append(str(row) + "_" + str(col))
        	nr_training = len(X_train)
        	train_start = 1
        	train_stop = burst
    		while train_stop <= nr_training:
    			classifier.partial_fit(X_train[train_start:train_stop], Y_train[train_start:train_stop], classes)
    			train_start = train_stop + 1
    			train_stop = train_start + burst - 1
    			if train_stop > nr_training:
    				train_stop = nr_training
    			if train_start >= nr_training:
    				train_stop = nr_training + 1
    	else:
        	classifier.fit(X_train, Y_train)
        
        #save classifier 
        joblib.dump(classifier, base_path + 'data/' + algorithm + '-' + str(ps[psi]) + '.pkl')  
    
        # store classes
        ordered_y = sorted(set(Y_train))
        
        
        joblib.dump(ordered_y, base_path + 'data/classes-' + algorithm + '-' + str(ps[psi]) + '.pkl')    
      
    
        accuracy = classifier.score(X_test, Y_test)
        Y_pred = classifier.predict(X_test)
          
        out_file = open(base_path + "data/test-" + algorithm + '-' + str(ps[psi]) + '.txt',"w")
        
        out_file.write(str(ps[psi]) + " Precision macro: %1.3f" % precision_score(Y_test, Y_pred,average='macro') + "\n")
        out_file.write(str(ps[psi]) + " Precision micro: %1.3f" % precision_score(Y_test, Y_pred,average='micro') + "\n")
        out_file.write(str(ps[psi]) + " Precision weighted: %1.3f" % precision_score(Y_test, Y_pred,average='weighted') + "\n")
         
        out_file.write(str(ps[psi]) + " Recall macro: %1.3f" % recall_score(Y_test, Y_pred, average='macro') + "\n")
        out_file.write(str(ps[psi]) + " Recall micro: %1.3f" % recall_score(Y_test, Y_pred, average='micro') + "\n")
        out_file.write(str(ps[psi]) + " Recall weighted: %1.3f" % recall_score(Y_test, Y_pred, average='weighted') + "\n")
        
        out_file.write("Accuracy:   %.3f" % accuracy  + "\n")
        out_file.close()
        

