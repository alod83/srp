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
        'record_id',
        'mmsi',
        'date_time',
        'ST_X (ST_Transform (geom, 4326))', # longitude
        'ST_Y (ST_Transform (geom, 4326))', # latitude
        'speed',
        'heading',
        'abs(b+a)', # length
        'abs(d+c)',  # width
        'basic_class',
    ]
    
    features = [
        'ST_Y (ST_Transform (geom, 4326))', 
        'ST_X (ST_Transform (geom, 4326))',
        'heading', 
        'speed',
        'basic_class'
    ]
    
    burst = 10000
    
    # init object by opening a MySQL connection
    def __init__(self):
        mp = get_mysql()
        self.cnx = psycopg2.connect(user=mp['user'], password=mp['password'],database=mp['db'])
        self.table = mp['table']
        self.trs = get_training_set()
        self.gp = get_grid()
        self.ft = get_features()
        # TODO correct prediction_steps
        self.next_status = []
        self.ps = []
        for i in range(0,len(self.trs['prediction_steps'])):
            self.ps.insert(i,str(self.trs['prediction_steps'][i]))
            self.next_status.insert(i,"next_status_" + self.ps[i])
        
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
    def get_all_from_table(self,condition=False):
        if condition is False:
            condition = "true"
        cursor = self.select(self.table, self.lf, condition)
        return self.cursor_to_list(cursor,self.lf)
    
    def build_datasets(self,extract_test=False, start_index=False, end_index=False,continue_from_previous_run=False):
        # split the dataset in training and test
        # calculate also the next step
        for cps in range(0,len(self.ps)):
            condition = "true"
            if start_index is not False and end_index is not False:
                condition = "record_id >= " + str(start_index) + " and record_id <= " + str(end_index)
            if continue_from_previous_run == True:
                condition = condition + " and " + self.next_status[cps] + " == -1"
            rows = self.get_all_from_table(condition)
            nr = len(rows) 
#            il = []
#             if extract_test == True:
#                 #self.set_all_training(condition)
#                 p = self.trs['percentage']
#                 ne = int(nr - float(nr)/100*int(p))     # number of extractions
#                 # build test set (as default, all values belong to the training set)
#                 # list of indexes used for the training set
#                 index = 0
#                 for i in range(0,ne):
#                     # extract a number until it is already contained in the il
#                     while index in il:
#                         index = random.randint(0,nr-1)
#                     il.append(index) 
#                     nsi = self.get_next_status(rows[index],self.ps[cps]) # index of the next status
#                     if nsi is None:
#                         nsi = -1
#                     # TESTSET -> dataset = false
#                     # is_small
#                     length = rows[index]['abs(b+a)']
#                     width = rows[index]['abs(d+c)']
#                     bc = self.get_basic_class(length, width)
#                     self.update(self.table,"is_training = false, " + self.next_status[cps] + " = " + str(nsi)  + ", basic_class = " + str(bc) , "record_id = " + str(rows[index]['record_id']) + "")    
#             
            # update next status also for trainig set
            bc = 0
            for i in range(0,nr):
                #if i not in il:
                nsi = self.get_next_status(rows[i],self.ps[cps])
                if nsi is None:
                    nsi = -1
                if rows[i]['abs(b+a)'] is None:
                    bc = -1
                else:
                    length = float(rows[i]['abs(b+a)'])
                    width = float(rows[i]['abs(d+c)'])
                    bc = self.get_basic_class(length, width)
                self.update(self.table, self.next_status[cps] + " = " + str(nsi) + ", basic_class = " + str(bc) , "record_id =" + str(rows[i]['record_id']) + "")    
    
    def get_basic_class(self, length, width):
        if length <= float(self.ft['small_ship_length']):
            return 0 # small ship class 0
        if length >= float(self.ft['big_ship_length']):
            return 1 # big ship class 2
        return 2 # medium ship class 1
        
             
    def get_next_status(self, row,ps):
        name = row['mmsi']
        ts = row['date_time']
        ps = int(ps)*60
        epsilon = ps/3
        sstep = ps - epsilon
        estep = ps + epsilon
    
        # do not choose the first one (ORDER BY date_time ASC) but the nearest to the prediction step 
        #condition = "mmsi = '" + row['mmsi'] + "' AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) >= " + str(sstep) + " AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) <= " + str(estep) + " ORDER BY date_time ASC LIMIT 1" 
        condition = "mmsi = '" + row['mmsi'] + "' AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) >= " + str(sstep) + " AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) <= " + str(estep) + " ORDER BY  abs(EXTRACT(EPOCH FROM (date_time - (timestamp '" + str(ts) + "' + interval '" + str(ps) + " seconds')))) ASC LIMIT 1" 
        
        cursor = self.select(self.table, self.lf, condition)
        next = cursor.fetchone()
        if next is None:
            return None
        return next[0]    
    
#     def get_dataset(self,type,psi,start_index=False,end_index=False):
#         # return a x and y
#         fields = []
#         for feature in self.features:
#             fields.append(feature)
#         fields.append(self.next_status[psi])
#         condition = "is_training = " + type + " AND " + self.next_status[psi] + " != -1"
#         if start_index is not False and end_index is not False:
#             condition = condition + " AND record_id >= " + str(start_index) + " and record_id < " + str(end_index)
#         
#         cursor = self.select(self.table, fields, condition)
#         rows = self.cursor_to_list(cursor,fields)
#         
#         X = []
#         y = []
#         
#         nf = ['ST_Y (ST_Transform (geom, 4326))', 'ST_X (ST_Transform (geom, 4326))']  # next fields
#         for row in rows:
#             if row[self.next_status[psi]] is not -1 and row[self.next_status[psi]] is not 0:
#                 f = []
#                 for feature in self.features:
#                     # if feature is course, modify it to use cos and sin
#                     if feature == 'heading':
#                         f.append(math.sin(float(row[feature])))
#                         f.append(math.cos(float(row[feature])))
#                     else:    
#                         f.append(float(row[feature]))
#                 X.append(f)
#                     
#                 # get next position
#                 condition = "record_id = " + str(row[self.next_status[psi]])
#                 cursor = self.select(self.table, nf, condition)
#                 next = cursor.fetchone()
#                 #print row['next_status']
#                 #print next
#                 nlat = float(next[0])
#                 nlng = float(next[1])
#                 [nx,ny] = get_position_in_grid(nlng, nlat, float(self.gp['cx']), float(self.gp['cy']))
#                 y.append(str(int(ny)) + "_" + str(int(nx)))
#         X = np.asarray(X)
#         y = np.asarray(y)
#         return X,y
    
    def get_dataset(self,psi,start_index=False,end_index=False):
        # return a x and y
        fields = []
        for feature in self.features:
            fields.append(feature)
        fields.append(self.next_status[psi])
        condition = self.next_status[psi] + " != -1"
        if start_index is not False and end_index is not False:
            condition = condition + " AND record_id >= " + str(start_index) + " and record_id < " + str(end_index)
         
        cursor = self.select(self.table, fields, condition)
        rows = self.cursor_to_list(cursor,fields)
         
        X = []
        y = []
         
        nf = ['ST_Y (ST_Transform (geom, 4326))', 'ST_X (ST_Transform (geom, 4326))']  # next fields
        for row in rows:
            if row[self.next_status[psi]] is not -1 and row[self.next_status[psi]] is not 0:
                f = []
                for feature in self.features:
                    # if feature is course, modify it to use cos and sin
                    if feature == 'heading':
                        f.append(math.sin(float(row[feature])))
                        f.append(math.cos(float(row[feature])))
                    else:    
                        f.append(float(row[feature]))
                X.append(f)
                     
                # get next position
                condition = "record_id = " + str(row[self.next_status[psi]])
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
    
    def get_prediction_steps(self):
        return self.trs['prediction_steps']
    
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
        #print query
        cursor = self.cnx.cursor()
        cursor.execute(query)
        self.cnx.commit()
        count = cursor.rowcount
        cursor.close()
        return count
     
    def set_all_training(self,where):
        set = "is_training = true"
        self.update(self.table,set,where)
        
    def get_n_features(self):
        return len(self.features)
    
    def close_cnx(self):
        self.cnx.close()   

