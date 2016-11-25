import psycopg2
# load mysql parameters
from config import get_mysql
from config import get_training_set
from config import get_features
from geo import get_position_in_grid
from config import get_grid
import numpy as np
import math

import random

# TODO Remove limit 3 from queries.
class MyAPI:
    
    lf = [
        'vessel_id',
        'mmsi',
        'date_time',
        'ST_X (ST_Transform (geom, 4326))', # longitude
        'ST_Y (ST_Transform (geom, 4326))', # latitude
        'speed',
        'course',
        'abs(b-a)', # length
        'abs(d-c)'  # width
        'basic_class',
    ]
    
    features = [
        'ST_Y (ST_Transform (geom, 4326))', 
        'ST_X (ST_Transform (geom, 4326))',
        'course', 
        'speed',
        'basic_class'
    ]
    
    # init object by opening a MySQL connection
    def __init__(self):
        mp = get_mysql()
        self.cnx = psycopg2.connect(user=mp['user'], password=mp['password'],database=mp['db'])
        self.table = mp['table']
        self.trs = get_training_set()
        self.gp = get_grid()
        self.ft = get_features()
        self.next_status = "next_status_" + self.trs['prediction_step']
        
    def select(self,table, fields, condition):
        query = "SELECT "
        for field in fields:
            query = query + field + ", "
        query = query[:-2] + " FROM " + table + " WHERE " + condition
        #print query
        #cursor = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        cursor.execute(query)
        return cursor
    
    def cursor_to_list(self,cursor,fields):
        result = []
        row = cursor.fetchone()
        j = 0
        
        while row is not None:
            result.insert(j, dict())
            
            for i in range(0,len(fields)):
                result[j][fields[i]] = row[i]
                
            j = j + 1
            row = cursor.fetchone()
        return result
    
    # get all fields from table 
    def get_all_from_table(self):
        cursor = self.select(self.table, self.lf, "true")
        return self.cursor_to_list(cursor,self.lf)
    
    def build_datasets(self,extract_test=False):
        # split the dataset in training and test
        # calculate also the next step
        rows = self.get_all_from_table()
        nr = len(rows)   
        il = []
        if extract_test == True:
            p = self.trs['percentage']
            ne = nr - nr/100*int(p)      # number of extractions
            
            # build test set (as default, all values belong to the training set)
            # list of indexes used for the training set
            index = 0
            for i in range(0,ne):
                # extract a number until it is already contained in the il
                while index in il:
                    index = random.randint(0,nr-1)
                il.append(index) 
                nsi = self.get_next_status(rows[index]) # index of the next status
                if nsi is None:
                    nsi = -1
                # TESTSET -> dataset = false
                # is_small
                length = rows[index]['abs(b-a)']
                width = rows[index]['abs(d-c)']
                bc = self.get_basic_class(length, width)
                self.update(self.table,"is_training = false, " + self.next_status + " = " + str(nsi)  + ", basic_class = " + str(bc) , "vessel_id ='" + str(rows[index]['vessel_id']) + "'")    
        
        # update next status also for trainig set
        for i in range(0,nr):
            if i not in il:
                nsi = self.get_next_status(rows[i])
                if nsi is None:
                    nsi = -1
                length = float(rows[i]['abs(b-a)'])
                width = float(rows[i]['abs(d-c)'])
                bc = self.get_basic_class(length, width)
                self.update(self.table,self.next_status + " = " + str(nsi) + ", basic_class = " + str(bc) , "vessel_id ='" + str(rows[i]['vessel_id']) + "'")    
    
    def get_basic_class(self, length, width):
        if length <= float(self.ft['small_ship_length']) and width <= float(self.ft['small_ship_width']):
            return 0 # small ship class 0
        if length >= float(self.ft['big_ship_length']) and width >= float(self.ft['big_ship_width']):
            return 2 # big ship class 2
        return 1 # medium ship class 1
        
             
    def get_next_status(self, row):
        name = row['mmsi']
        ts = row['date_time']
        sstep = int(self.trs['prediction_step'])*60
        estep = 2*sstep
        condition = "mmsi = '" + row['mmsi'] + "' AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) >= " + str(sstep) + " AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) <= " + str(estep) + " ORDER BY date_time ASC LIMIT 1" 
        cursor = self.select(self.table, self.lf, condition)
        next = cursor.fetchone()
        if next is None:
            return None
        return next[0]    
    
    def get_dataset(self,type):
        # return a x and y
        fields = []
        for feature in self.features:
            fields.append(feature)
        fields.append(self.next_status)
        cursor = self.select(self.table, fields, "is_training = " + type + " AND " + self.next_status + " != -1")
        rows = self.cursor_to_list(cursor,fields)
        
        X = []
        y = []
        
        nf = ['ST_Y (ST_Transform (geom, 4326))', 'ST_X (ST_Transform (geom, 4326))']  # next fields
        for row in rows:
            if row[self.next_status] is not -1:
                f = []
                for feature in self.features:
                    # if feature is course, modify it to use cos and sin
                    if feature == 'course':
                        f.append(math.sin(float(row[feature])))
                        f.append(math.cos(float(row[feature])))
                    else:    
                        f.append(float(row[feature]))
                X.append(f)
                    
                # get next position
                condition = "vessel_id = " + str(row[self.next_status])
                cursor = self.select(self.table, nf, condition)
                next = cursor.fetchone()
                #print row['next_status']
                #print next
                nlat = float(next[0])
                nlng = float(next[1])
                [nx,ny] = get_position_in_grid(nlng, nlat, float(self.gp['cx']), float(self.gp['cy']))
                y.append(str(int(ny)) + "_" + str(int(nx)))
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
            'table'     : self.table,
            'fields'    : fields,
            'values'    : vs
        }
        query = "INSERT INTO %(table)s (%(fields)s) VALUES (%(values)s)" %(data)
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
        cursor = self.cnx.cursor()
        cursor.execute(query)
        self.cnx.commit()
        count = cursor.rowcount
        cursor.close()
        return count
     
    
    def close_cnx(self):
        self.cnx.close()   

