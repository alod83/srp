import mysql.connector as mysql
import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))
from conn import MyConn

SQLObj = MyConn()
# set pattern ID
SQLObj.set_pattern_id()
# set reflection ID
patterns = {}
id_count = 0
pattern_id = 0
rows = SQLObj.get_pattern()
for row in rows:
    pattern = row['pattern']
    try:
        pattern_id = patterns[pattern]
    except KeyError:
        id_count = id_count + 1
        patterns[pattern] = id_count
        pattern_id = patterns[pattern]
    
    set = "pattern_id = " + str(pattern_id)
    where = "pattern = '" + pattern + "'"
    SQLObj.update("Pattern", set,where)

SQLObj.close_cnx()
