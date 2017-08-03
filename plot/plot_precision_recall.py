print(__doc__)

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle
from sklearn.externals import joblib
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn import svm, datasets
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_recall_fscore_support

import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))

from MyAPI import MyAPI

algorithms = ["knn", "one-vs-rest", "mlp", "decision-tree"]
colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])
lw = 2
    
ps = "30"
plt.clf()
for algorithm, color in zip(algorithms, colors):

    # carico il classificatore
    classifier = joblib.load('data/binarize/' + algorithm + '-' + ps + '.pkl') 
    # carico i dati di test
    random_state = np.random.RandomState(0)
    api = MyAPI()
    X, y = api.get_dataset(0, start_index=0,end_index=20, nr=20)
    # binarizzo y
    classes = joblib.load('data/binarize/classes-' + algorithm + '-' + ps + '.pkl') 
    
    y= label_binarize(y, classes=classes)
    #print range(0,len(y)-1)
    # restore classes from file
     
     
    #n_classes = y.shape[1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.9,
                                                        random_state=random_state)
    # restore robust scaler from file
    robust_scaler = joblib.load('data/binarize/rs-' + algorithm + '-' + ps + '.pkl') 
        
    
    #n_classes = list(set(y_test))
    # uso la predict/decision_function
    X_test = robust_scaler.transform(X_test)
    y_score = classifier.predict(X_test)
    
    precision, recall, _ = precision_recall_curve(y_test.ravel(),y_score.ravel())
    #average_precision[type] = average_precision_score(y_test, y_score,
        #                                                 average=type)
    plt.plot(recall, precision, color=color, lw=lw,label=algorithm)


plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(loc="lower right")
plt.savefig('plot-knn.png')

