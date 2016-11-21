from MyAPI import MyAPI

import numpy as np
import dill

api = MyAPI()
X,y = api.get_dataset('TRAINING') 

# apply feature scaling to X
scaler = MinMaxScaler(feature_range=(-1, 1))
scaler.fit(X)  
scaler.transform(X) 

# encode labels
le = LabelEncoder()
# retrieve all the classes
#take y list, order and remove duplicates
#classes = sorted(set(y))

le.fit(y)  
# save label matrix
# store the object on file
with open('labels.pkl', 'wb') as f:
    dill.dump(le, f)


n_hidden_layers = len(X[0]) - 1
current_layer = n_hidden_layers
hidden_layer = []
while current_layer > 1:
    hidden_layer.append(current_layer)
    current_layer = current_layer - 1

clf = MLPClassifier(solver='lbfgs', alpha=0.0001, hidden_layer_sizes=hidden_layer,random_state=1)
parameters = {'alpha'           : 10.0 ** -np.arange(1, 7), 
              'solver'          : ['lbfgs', 'sgd', 'adam'],
              'activation'      : ['identity', 'logistic', 'tanh', 'relu'],
              'learning_rate'   : ['constant', 'invscaling', 'adaptive']
            }

# search best param
#gs = GridSearchCV(clf, parameters)
#gs.fit(X, y)
#print(gs.best_estimator_)

#clf.set_params(gs.best_estimator_)
clf = clf.fit(X, y)

# store the object on file
with open('training_set.pkl', 'wb') as f:
    dill.dump(clf, f)