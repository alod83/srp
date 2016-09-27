# This script splits the time in slots of 1 hour

from datetime import datetime
import mysql.connector as mysql
import os
import sys
config_path = "../../utilities/"
sys.path.append(os.path.abspath(config_path))
from utilities import myquery
from config import get_mysql
from utilities import myquery

mp = get_mysql()
cnx = mysql.connect(user=mp['user'], password=mp['password'],database=mp['db'])

# select all the timestamps
query = "SELECT MMSI,TIMESTAMP FROM " + mp['locality']
cursor = myquery(cnx,query)
row = cursor.fetchone()
while row is not None:
    date = row[1]
    # starting and end hours
    sh = date.hour
    eh = (date.hour+1)%24
    
    # insert values in table timestamp
    data = {
    'locality' : mp['locality'],
    'mmsi': str(row[0]),
    'year': date.year,
    'month': date.month,
    'day': date.day,
    'sh': sh,
    'eh': eh,
    }
    
    iq = "INSERT INTO %(locality)s_Timestamp (vessel_id, year, month, day,sh,eh) VALUES (%(mmsi)s, %(year)s, %(month)s, %(day)s, %(sh)s, %(eh)s)" %(data)
    ic = myquery(cnx,iq)
    ic.close()
    cnx.commit()
    row = cursor.fetchone()
cursor.close()
cnx.close()



