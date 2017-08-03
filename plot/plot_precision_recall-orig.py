print(__doc__)

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle

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

api = MyAPI()
X, y = api.get_dataset(0, start_index=0,end_index=10000, nr=10000)

# setup plot details
colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])
lw = 2

y= label_binarize(y, classes=list(set(y)))

#print range(0,len(y)-1)

n_classes = y.shape[1]
# import some data to play with


random_state = np.random.RandomState(0)
n_samples, n_features = X.shape

# Split into training and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2,
                                                    random_state=random_state)
classifier = KNeighborsClassifier(weights='distance',n_neighbors=3)
y_score = classifier.fit(X_train, y_train).predict(X_test)
# Compute Precision-Recall and plot curve

precision = dict()
recall = dict()
average_precision = dict()
print n_classes

plt.clf()
colors = {'micro' : 'red', 'macro': 'blue'}
for type in ["macro", "micro"]:
    print type
    precision[type], recall[type], _ = precision_recall_curve(y_test.ravel(),y_score.ravel())
    print recall[type]
    #average_precision[type] = average_precision_score(y_test, y_score,
    #                                                 average=type)
    plt.plot(recall[type], precision[type], color=colors[type], lw=lw,
         label=type+'-average Precision-recall curve')


plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Extension of Precision-Recall curve to multi-class')
plt.legend(loc="lower right")
plt.savefig('plot-knn.png')

