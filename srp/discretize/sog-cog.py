# This script maps vessels speed/course in speed/course slots

import mysql.connector as mysql
import os
import sys
config_path = "../../utilities/"
sys.path.append(os.path.abspath(config_path))

from utilities import myquery
# * * * * * LOAD PARAMETERS FROM CONFIG FILE * * * * *
# load mysql parameters
from config import get_mysql

# * * * * * END LOAD PARAMETERS FROM CONFIG FILE * * * * *


def populate(type):
    mp = get_mysql()
    cnx = mysql.connect(user=mp['user'], password=mp['password'],database=mp['db'])
    
    # select all the speed/course ranges
    query = "SELECT id,min,max FROM " + type
    cursor = myquery(cnx,query)
    row = cursor.fetchone()
    while row is not None:
        min = int(row[1])
        max = int(row[2])
        sd = {
        'type' : type.upper(),
        'locality': mp['locality'],
        'min': min,
        'max': max,
        }
    
        sq = "SELECT MMSI, %(type)s FROM %(locality)s WHERE %(type)s >= '%(min)s' AND %(type)s < '%(max)s'" % (sd)
        sc = myquery(cnx,sq)
        srow = sc.fetchone()
        while srow is not None:
            id = {
            'type' : type,
            'locality' : mp['locality'],
            'vessel_id' : srow[0],
            'id' : row[0],
            }
            iq = "INSERT INTO %(locality)s_%(type)s(vessel_id,%(type)s_id) VALUES('%(vessel_id)s', '%(id)s')" % (id)
            ic = myquery(cnx,iq)
            ic.close()
            cnx.commit()
            srow = sc.fetchone()
        sc.close()
        row = cursor.fetchone()
    cursor.close()
    cnx.close()
    return

populate("Speed")
populate("Course")
