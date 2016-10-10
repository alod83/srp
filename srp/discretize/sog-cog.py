# This script maps vessels speed/course in speed/course slots

import mysql.connector as mysql
import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))

from conn import MyConn

def populate(type):
    SQLObj = MyConn()
    
    rows = SQLObj.get_min_max_from_type(type)
    for row in rows:
        min = int(row['min'])
        max = int(row['max'])
        
        srows = SQLObj.get_type_ranges_from_locality(type, min,max)
        for srow in srows:
            values = [srow['MMSI'],row['id']]
            SQLObj.set_type(values,type)
    return

populate("Speed")
populate("Course")
