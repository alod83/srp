import numpy as np

def concatenate(x1,x2):
    if  len(x1) == 0:
        return x2
    else:
        return np.concatenate((x1, x2), axis=0)
