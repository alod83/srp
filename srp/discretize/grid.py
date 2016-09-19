# This script transforms each coordinate (latitude, longitude) in a
# position (row, column) in the grid

import mysql.connector as mysql
import os
import sys
config_path = "../../utilities/"
sys.path.append(os.path.abspath(config_path))


# TODO move templates to utilities
geo_path = "../../../templates/python/geo/"
sys.path.append(os.path.abspath(geo_path))
from geo import get_position_in_grid
from utilities import myquery

# ctype = category type (latitude or longitude)
# otype = operation type (max or min)
def get_boundary(ctype,otype,cnx,table):
    query = ("SELECT " + otype + "(" + ctype.upper() + ") FROM " + table)
    cursor = myquery(cnx,query)
    row = cursor.fetchone()
    cursor.close()
    return float(row[0])

# * * * * * LOAD PARAMETERS FROM CONFIG FILE * * * * *
# load mysql parameters
from config import get_mysql
mp = get_mysql()

# load grid parameters parameters from config.ini
from config import get_grid
gp = get_grid()
# * * * * * END LOAD PARAMETERS FROM CONFIG FILE * * * * *

cnx = mysql.connect(user=mp['user'], password=mp['password'],database=mp['db'])

# retrieve minimum latitude and longitude to build the grid
min_lat = get_boundary("LATITUDE", "MIN", cnx, mp['locality'])
min_long = get_boundary("LONGITUDE", "MIN", cnx,mp['locality'])

query = "SELECT MMSI,LATITUDE,LONGITUDE,TIMESTAMP,NAME FROM " + mp['locality']
cursor = myquery(cnx,query)
row = cursor.fetchone()
while row is not None:
    [x, y] = get_position_in_grid(float(row[1]), float(row[2]), float(gp['cx']), float(gp['cy']), min_lat, min_long)
    # Insert data information
    data = {
    'locality' : mp['locality'],
    'mmsi': str(row[0]),
    'row': str(x),
    'col': str(y),
    'timestamp': str(row[3]),
    'name': str(row[4]),
    }
    
    iq = "INSERT INTO %(locality)s_Grid (MMSI, row, col, timestamp,name) VALUES (%(mmsi)s, %(row)s, %(col)s, '%(timestamp)s', '%(name)s')" %(data)

    ic = myquery(cnx,iq)
    ic.close()
    cnx.commit()
    row = cursor.fetchone()
cursor.close()
cnx.close()
