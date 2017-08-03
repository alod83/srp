#!/bin/bash

#python train.py -a knn &
python train.py -a one-vs-one &
python train.py -a one-vs-rest &
#python train.py -a gaussian-nb -c &
#python train.py -a bernoulli-nb -c &
#python train.py -a decision-tree &
python train.py -a svm &
python train.py -a linear-svm &
python train.py -a mlp &
python train.py -a radius-neighbor & #current
#python train.py -a sgd -c &
#python train.py -a kernel-approx &
