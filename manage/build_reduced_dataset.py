# Questo script costruisce una versione ridotta del dataset.
# Il dataset ridotto individua una specifica area della griglia
# delimitata da min row e max row, min col e max col
# per ogni cella del dataset ridotto estrae X campioni a caso e li memorizza nella tabella

import argparse
import os
import sys
config_path = "../srp/utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI

parser = argparse.ArgumentParser(description='Reduced Table Builder')
parser.add_argument('-n', '--samples',help='The number of samples to be extracted for each cell',required=True)

args = parser.parse_args()

n_samples = args.samples
print n_samples

min_row = 349
max_row = 358
min_col = 146
max_col = 155

api = MyAPI()
api.build_reduced_dataset(min_row,max_row,min_col,max_col,n_samples)
api.discretize("srp_reduced")
