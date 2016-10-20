#import mysql.connector as mysql
import os
import sys
config_path = "../utilities/"
sys.path.append(os.path.abspath(config_path))
from conn import MyConn
from fp_growth import find_frequent_itemsets

SQLObj = MyConn()
rows = SQLObj.get_pattern()
transactions = {}
for row in rows:
    name = row['name']
    pattern = row['pattern_id']
    
    try:
        transactions[name].append(pattern)
    except KeyError:
        transactions[name] = [pattern]
    
transactions = [list(v) for k,v in transactions.items()]

minsup = 10
itemset_id = 1
for itemset in find_frequent_itemsets(transactions, minsup):
    for item in itemset:
        values = [itemset_id,item ]
        SQLObj.set_itemset(values)
    itemset_id = itemset_id + 1
SQLObj.close_cnx()