# This script implements the Market Basket Analysis algorithms

import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))
from conn import MyConn

SQLObj = MyConn()
patterns = SQLObj.get_pattern(True)
confidence = 0
for antl in patterns:
    ant = antl['distinct pattern_id']
    # number of antecedents
    na = SQLObj.count_items(ant)
    for consl in patterns:
        cons = consl['distinct pattern_id']
        if na != 0:
            # number of antecedents and consequents
            nac = SQLObj.count_items(ant,cons)
            confidence  = float(nac) / float(na) 
        values = [ant,cons, confidence]
        SQLObj.set_confidence(values) 