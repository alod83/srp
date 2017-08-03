from sklearn.externals import joblib
import os.path
import sys
 
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))
from config import get_training_set

from sklearn.neighbors import KNeighborsClassifier
 
 
tp = get_training_set()
ps = tp['prediction_steps']
algorithms = ['knn', 'bernoulli-nb', 'kernel-approx', 'sgd', 'linear-svm', 'one-vs-rest', 'decision-tree']
for algo in algorithms:
    for psi in ps:
        print("Algorithm: " + algo + " Step: " + str(psi))
        path = 'data/best-estimator-' + algo + '-'+ str(psi) + '.pkl'
        classifier = joblib.load(path)
        print(classifier) 
        print("\n")
    print("* * * * *\n")
         
