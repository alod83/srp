# This script transforms each coordinate (latitude, longitude) in a
# position (row, column) in the grid

import mysql.connector as mysql
import os
import sys

geo_path = "../../templates/python/geo/"
sys.path.append(os.path.abspath(geo_path))
from geo import get_position_in_grid

def myquery(cnx,query):
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    return cursor

# ctype = category type (latitude or longitude)
# otype = operation type (max or min)
def get_boundary(ctype,otype,cnx):
    query = ("SELECT " + otype + "(" + ctype.upper() + ") FROM Malta")
    cursor = myquery(cnx,query)
    row = cursor.fetchone()
    cursor.close()
    return float(row[0])


cnx = mysql.connect(user='root', password="",database='DATI_AIS')

# retrieve minimum latitude and longitude to build the grid
min_lat = get_boundary("LATITUDE", "MIN", cnx)
min_long = get_boundary("LONGITUDE", "MIN", cnx)

# define step
cx = 0.1
cy = 0.1

insert_structure = ("INSERT INTO Malta_Grid "
              "(MMSI, row, col, timestamp,name) "
              "VALUES (%(mmsi)s, %(row)s, %(col)s, %(timestamp)s, %(name)s)")

query = "SELECT MMSI,LATITUDE,LONGITUDE,TIMESTAMP,NAME FROM Malta"
cursor = myquery(cnx,query)
row = cursor.fetchone()
while row is not None:
    [x, y] = get_position_in_grid(float(row[1]), float(row[2]), cx, cy, min_lat, min_long)
    # Insert data information
    data = {
    'mmsi': str(row[0]),
    'row': str(x),
    'col': str(y),
    'timestamp': str(row[3]),
    'name': str(row[4]),
    }
    
    ic = cnx.cursor(buffered=True)
    ic.execute(insert_structure,data)
    ic.close()
    cnx.commit()
    row = cursor.fetchone()
cursor.close()
cnx.close()