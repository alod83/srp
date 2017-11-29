#!/bin/bash

training_set_size=(2000000 4000000 8000000 16000000)

for i in "${training_set_size[@]}" 
do
   echo $i
   python train.py -n $i -t 250000 -b 1
   mkdir data/knn-$i
   python predict.py -v features -l 32.5 -n 12.2 -b 0 -s 0.5 -c 130 > data/knn-$i/output-predict.txt
   mv data/*knn*.pkl data/knn-$i
   mv data/*knn*.txt data/knn-$i
done