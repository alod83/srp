import mysql.connector as mysql
# load mysql parameters
from config import get_mysql
from config import get_training_set
from geo import get_position_in_grid
from config import get_grid
import numpy as np

import random

# TODO Remove limit 3 from queries.
class MyAPI:
    
    lf = [
        'vessel_id',
        'MMSI',
        'TIME',
        'TIMESTAMP',
        'LATITUDE',
        'LONGITUDE',
        'NAME',
        'SPEED',
        'COURSE'
    ]
    
    features = [
        'LATITUDE', 
        'LONGITUDE',
        'COURSE', 
        'SPEED'
    ]
    
    # init object by opening a MySQL connection
    def __init__(self):
        mp = get_mysql()
        self.cnx = mysql.connect(user=mp['user'], password=mp['password'],database=mp['db'])
        self.locality = mp['locality']
        self.trs = get_training_set()
        self.gp = get_grid()
        
    def select(self,table, fields, condition):
        query = "SELECT "
        for field in fields:
            query = query + field + ", "
        query = query[:-2] + " FROM " + table + " WHERE " + condition
        #print query
        cursor = self.cnx.cursor(buffered=True)
        cursor.execute(query)
        return cursor
    
    def cursor_to_list(self,cursor,fields):
        result = []
        row = cursor.fetchone()
        j = 0
#         minl = {}
#         maxl = {}
#         for i in fields:
#             minl[i] = 10000
#             maxl[i] = 0
        
        while row is not None:
            result.insert(j, dict())
            
            for i in range(0,len(fields)):
                #d_row = float(row[i])
                result[j][fields[i]] = row[i]
#                 if d_row < minl[fields[i]]:
#                     minl[fields[i]] = d_row
#                 if d_row > maxl[fields[i]]:
#                     maxl[fields[i]] = d_row
                
            j = j + 1
            row = cursor.fetchone()
        return result
    
    # get all fields from table 
    def get_all_from_locality(self):
        cursor = self.select(self.locality, self.lf, "1")
        return self.cursor_to_list(cursor,self.lf)
    
    def build_datasets(self):
        # split the dataset in training and test
        # calculate also the next step
        rows = self.get_all_from_locality()
        p = self.trs['percentage']
        
        nr = len(rows)               # number of rows
        ne = nr - nr/100*int(p)      # number of extractions
        
        # build test set (as default, all values belong to the training set)
        il = []         # list of indexes used for the training set
        index = 0
        for i in range(0,ne):
            # extract a number until it is already contained in the il
            while index in il:
                index = random.randint(0,nr-1)
            il.append(index) 
            nsi = self.get_next_status(rows[index]) # index of the next status
            if nsi is None:
                nsi = -1
            self.update(self.locality,"DATASET = 'TEST', NEXT_STATUS = " + str(nsi) , "vessel_id ='" + str(rows[index]['vessel_id']) + "'")    
        # update next status also for trainig set
        for i in range(0,nr):
            if i not in il:
                nsi = self.get_next_status(rows[i])
                if nsi is None:
                    nsi = -1
                self.update(self.locality,"NEXT_STATUS = " + str(nsi) , "vessel_id ='" + str(rows[i]['vessel_id']) + "'")    
         
    def get_next_status(self, row):
        name = row['NAME']
        ts = row['TIMESTAMP']
        sstep = self.trs['prediction_step']
        estep = 2*int(sstep)
        condition = "NAME = '" + row['NAME'] + "' AND TIMESTAMPDIFF(minute, '" + str(ts) + "', TIMESTAMP) >= " + sstep + " AND TIMESTAMPDIFF(minute, '" + str(ts) + "', TIMESTAMP) <= " + str(estep) + " ORDER BY TIMESTAMP ASC LIMIT 1" 
        cursor = self.select(self.locality, self.lf, condition)
        next = cursor.fetchone()
        if next is None:
            return None
        return next[0]    
    
    def get_dataset(self,type):
        # return a x and y
        fields = []
        for feature in self.features:
            fields.append(feature)
        fields.append('NEXT_STATUS')
        cursor = self.select(self.locality, fields, "DATASET = '" + type + "'")
        rows = self.cursor_to_list(cursor,fields)
        
        X = []
        y = []
        
        
        nf = ['LATITUDE', 'LONGITUDE']  # next fields
        for row in rows:
            if row['NEXT_STATUS'] is not -1:
                f = []
                for feature in self.features:
                    # feature scaling
                    #value = (float(row[feature]) - minl[feature])/ (maxl[feature]-minl[feature])
                    f.append(float(row[feature]))
                X.append(f)
                    
                # get next position
                condition = "vessel_id = " + str(row['NEXT_STATUS'])
                cursor = self.select(self.locality, nf, condition)
                next = cursor.fetchone()
                #print row['NEXT_STATUS']
                #print next
                nlat = float(next[0])
                nlng = float(next[1])
                [nx,ny] = get_position_in_grid(nlng, nlat, float(self.gp['cx']), float(self.gp['cy']))
                y.append(str(ny) + "_" + str(nx))
        X = np.asarray(X)
        y = np.asarray(y)
        return X,y
    
    def get_prediction_step(self):
        return int(self.trs['prediction_step'])
    
    def get_time_slot(self):
        return int(self.trs['time_slot'])
 
    # fields is a string, vaules is a list of values
    def insert(self,table,fields,values):
        vs = ""
        for i in range(0,len(values)):
            vs = vs + "'" + str(values[i]) + "',"
        #remove last comma
        vs = vs[:-1]
        data = {
            'locality'  : self.locality,
            'table'     : table,
            'fields'    : fields,
            'values'    : vs
        }
        query = "INSERT INTO %(locality)s_%(table)s (%(fields)s) VALUES (%(values)s)" %(data)
        cursor = self.cnx.cursor(buffered=True)
        cursor.execute(query)
        cursor.close()
        self.cnx.commit()
    
    def update(self,table,set,where=None):
        if where == None:
            where = "1"
        data = {
            'table'     : table,
            'set'       : set,
            'where'     : where
        }
        
        query = "UPDATE %(table)s SET %(set)s WHERE %(where)s" %(data)
        cursor = self.cnx.cursor(buffered=True)
        cursor.execute(query)
        self.cnx.commit()
        count = cursor.rowcount
        cursor.close()
        return count
     
    
    def close_cnx(self):
        self.cnx.close()   

