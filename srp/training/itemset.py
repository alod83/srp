#import mysql.connector as mysql
import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))
from conn import MyConn
from fp_growth import find_frequent_itemsets

SQLObj = MyConn()

time_slot = SQLObj.get_time_slot()
current_slot = 0
# number of slots in a day
while current_slot < 24:
    print current_slot
    rows = SQLObj.get_pattern(current_slot)
    transactions = {}
    for row in rows:
        name = row['name']
        pattern = row['pattern_id']
        
        try:
            transactions[name].append(pattern)
        except KeyError:
            transactions[name] = [pattern]
    
    transactions = [list(v) for k,v in transactions.items()]
    
    minsup = SQLObj.get_support()
    itemset_id = 1
    
    for itemset in find_frequent_itemsets(transactions, minsup):
        for item in itemset:
            values = [itemset_id,item,current_slot ]
            SQLObj.set_itemset(values)
        itemset_id = itemset_id + 1
        
    current_slot += time_slot
SQLObj.close_cnx()