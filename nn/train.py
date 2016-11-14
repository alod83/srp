from MyAPI import MyAPI
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler  
from sklearn.model_selection import GridSearchCV
import numpy as np
import dill

api = MyAPI()
X,y = api.get_training_set() 
# apply feature scaling
scaler = StandardScaler()
scaler.fit(X)  
X = scaler.transform(X)  
n_hidden_layers = len(X[0]) - 1
current_layer = n_hidden_layers
hidden_layer = []
while current_layer > 1:
    hidden_layer.append(current_layer)
    current_layer = current_layer - 1

clf = MLPClassifier(solver='lbfgs', alpha=0.001, hidden_layer_sizes=hidden_layer,random_state=1)
parameters = {'alpha'           : 10.0 ** -np.arange(1, 7), 
              'solver'          : ['lbfgs', 'sgd', 'adam'],
              'activation'      : ['identity', 'logistic', 'tanh', 'relu'],
              'learning_rate'   : ['constant', 'invscaling', 'adaptive']
            }

# search best param
gs = GridSearchCV(clf, parameters)
gs.fit(X, y)
print(gs.best_estimator_)

clf.set_params(gs.best_estimator_)
clf = clf.fit(X, y)

# store the object on file
with open('training_set.pkl', 'wb') as f:
    dill.dump(clf, f)