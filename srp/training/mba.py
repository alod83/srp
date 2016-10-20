# This script implements the Market Basket Analysis algorithms

import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))
from conn import MyConn

SQLObj = MyConn()
patterns = SQLObj.get_pattern(True)
for antl in patterns:
    ant = antl['distinct pattern_id']
    # number of antecedents
    na = SQLObj.count_items(ant)
    for consl in patterns:
        cons = consl['distinct pattern_id']
        # number of antecedents and consequents
        nac = SQLObj.count_items(ant,cons)
        confidence  = float(nac) / float(na) 
        print confidence
        values = [ant,cons, confidence]
        SQLObj.set_confidence(values) 