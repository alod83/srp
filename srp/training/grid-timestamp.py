# This script transforms each coordinate (latitude, longitude) in a
# position (row, column) in the grid

#import mysql.connector as mysql
import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))


# TODO move templates to utilities
geo_path = "../../../templates/python/geo/"
sys.path.append(os.path.abspath(geo_path))
from geo import get_position_in_grid
from conn import MyConn

# load grid parameters parameters from config.ini
from config import get_grid
gp = get_grid()
# * * * * * END LOAD PARAMETERS FROM CONFIG FILE * * * * *

SQLObj = MyConn()
rows = SQLObj.get_all_from_locality()

for row in rows:
    [x, y] = get_position_in_grid(float(row['LONGITUDE']), float(row['LATITUDE']), float(gp['cx']), float(gp['cy']))
   
    values = [
        row['MMSI'],
        y,
        x,
        row['TIMESTAMP'],
        row['NAME']
    ]
    SQLObj.set_grid(values)
    
    date = row['TIMESTAMP']
    # starting and end hours
    values = [
        row['MMSI'], 
        date.year,
        date.month,
        date.day,
        date.hour,
        (date.hour+1)%24   
    ]
    SQLObj.set_timestamp(values)
SQLObj.close_cnx()
 