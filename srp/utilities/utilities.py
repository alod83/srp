import numpy as np

def concatenate(x1,x2):
    if  len(x1) == 0:
        return x2
    else:
        return np.concatenate((x1, x2), axis=0)
        
def print_result(output,result):
	if output is None:
		print result
	else:
		with open(output, 'ab') as fh:
			fh.write(result)
