import psycopg2
from datetime import datetime
from datetime import timedelta
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
        'course',
        'abs(b+a)', # length
        'abs(d+c)',  # width
        'basic_class',
        'row',
        'col',
    ]
    
    lf_geom = [
        'record_id',
        'mmsi',
        'date_time',
        'geom',
        'speed',
        'course',
        'a',
        'b',
        'c',
        'd',
        'basic_class',
        'row',
        'col',
        'next_status_30',
        'next_status_45',
        'next_status_60'
    ]
    
    features = [
        'ST_Y (ST_Transform (geom, 4326))', 
        'ST_X (ST_Transform (geom, 4326))',
        #'row',
        #'col',
        'course', 
        'speed',
        #'discretized_speed',
        #'discretized_course',
        'basic_class'
    ]
    
    discretized_features = [
    	'row',
    	'col',
        'discretized_speed',
        'discretized_course',
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
    
    def get_grid_parameters(self):
        return self.gp
        
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
    
    def get_row_col_from_table(self, condition=False):
        if condition is False:
            condition = "true"
        lf = ['record_id', 'row', 'col']
        cursor = self.select(self.table, lf, condition)
        return self.cursor_to_list(cursor,lf)
    
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
                # add row and column
                lng = float(rows[i]['ST_X (ST_Transform (geom, 4326))']) # lng
                lat = float(rows[i]['ST_Y (ST_Transform (geom, 4326))']) # lat
                col, row = get_position_in_grid(lng,lat,float(self.gp['cx']),float(self.gp['cy']))
                rowcol = str(int(row)) + "_" + str(int(col))
                
                self.update(self.table, self.next_status[cps] + " = " + str(nsi) + ", basic_class = " + str(bc) + ",row = " + str(row) + ", col = " + str(col) + "" + ", row_col = '" + rowcol + "'", "record_id =" + str(rows[i]['record_id']) + "")    
    
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
        #epsilon = ps/3
        epsilon = 90
        sstep = ps - epsilon
        estep = ps + epsilon
        
        format = '%Y-%m-%d %H:%M:%S'
        #current_date = datetime.strptime(ts,format)
        next_sdate = ts + timedelta(seconds=sstep)
        next_edate = ts + timedelta(seconds=estep)
        next_cdate = ts + timedelta(seconds=ps)
    
        # do not choose the first one (ORDER BY date_time ASC) but the nearest to the prediction step 
        #condition = "mmsi = '" + row['mmsi'] + "' AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) >= " + str(sstep) + " AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) <= " + str(estep) + " ORDER BY date_time ASC LIMIT 1" 
        #condition = "mmsi = '" + row['mmsi'] + "' AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) >= " + str(sstep) + " AND EXTRACT(EPOCH FROM (date_time - '" + str(ts) + "')) <= " + str(estep) + " ORDER BY  abs(EXTRACT(EPOCH FROM (date_time - (timestamp '" + str(ts) + "' + interval '" + str(ps) + " seconds')))) ASC LIMIT 1" 
        condition = "mmsi = '" + row['mmsi'] + "' AND date_time >= '" + next_sdate.strftime(format) + "' AND date_time <= '" + next_edate.strftime(format) + "' ORDER BY  abs(EXTRACT(EPOCH FROM (date_time - (timestamp '" + next_cdate.strftime(format) + "')))) ASC LIMIT 1"
        cursor = self.select(self.table, self.lf, condition)
        next = cursor.fetchone()
        if next is None:
            return None
        return next[0]    
    
    
    def get_dataset(self,psi,start_index=False,end_index=False,nr=100000,table=False,external_condition=False,discretize=False,record_id=False):
        # return a x and y
        fields = []
        
        cfeatures = self.features
        if discretize is True:
        	cfeatures = self.discretized_features
        if table is False:
        	table = self.table
        for feature in cfeatures:
            fields.append(feature)
        fields.append(self.next_status[psi])
        #condition = self.next_status[psi] + " != -1 AND " + self.next_status[psi] + " IN (select " + str(self.next_status[psi]) + " from " + self.table + " where record_id <= " + str(nr) +" group by " + str(self.next_status[psi]) + " having count(" + str(self.next_status[psi]) + ") >= 5)"
        condition = self.next_status[psi] + " != -1"
        if external_condition is not False:
        	condition = condition + external_condition
        if start_index is not False and end_index is not False:
            condition = condition + " AND record_id >= " + str(start_index) + " and record_id <= " + str(end_index) 
        elif record_id is not False:
        	condition = "record_id = " + record_id
        cursor = self.select(table, fields, condition)
        rows = self.cursor_to_list(cursor,fields)
         
        X = []
        y = []
         
        nf = ['ST_Y (ST_Transform (geom, 4326))', 'ST_X (ST_Transform (geom, 4326))']  # next fields
        if discretize is True:
        	nf = ['row', 'col']
        for row in rows:
            if row[self.next_status[psi]] is not -1 and row[self.next_status[psi]] is not 0:
                f = []
                for feature in cfeatures:
                    # if feature is course, modify it to use cos and sin
                    if feature == 'course':
                        f.append(math.sin(float(row[feature])))
                        f.append(math.cos(float(row[feature])))
                    elif feature == 'basic_lass':
                        f.append(int(row[feature]))
                    elif (feature == 'discretized_speed') or (feature == 'discretized_course'):
                    	f.append(row[feature])
                    else:        
                        f.append(float(row[feature]))
                X.append(f)
                     
                # get next position
                condition = "record_id = " + str(row[self.next_status[psi]])
                cursor = self.select(self.table, nf, condition)
                next = cursor.fetchone()
                if next is None:
                	y.append("out_of_grid")
                else:
                	#print row['next_status']
               	 	#print next
                	nlat = float(next[0])
                	nlng = float(next[1])
                	[nx,ny] = get_position_in_grid(nlng, nlat, float(self.gp['cx']), float(self.gp['cy']))
                	#ny = next[0]
                	#nx = next[1]
                	y.append(str(int(ny)) + "_" + str(int(nx)))
                #y.append(str(ny) + "_" + str(nx))
        
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
            'table'     : table,
            'fields'    : fields,
            'values'    : vs
        }
        query = "INSERT INTO %(table)s (%(fields)s) VALUES (%(values)s)" %(data) 
        cursor = self.cnx.cursor()
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
        
    def set_grid_position(self, record_id, row, column):
        set = "row = '" + str(row) + "', col = '" + str(column) + "'"
        where = "record_id = " + str(record_id)
        self.update(self.table, set, where)
        
    def set_rowcol(self, record_id, rowcol):
        set = "row_col = '" + rowcol + "'"
        where = "record_id = " + str(record_id)
        self.update(self.table, set, where)
    
    def get_n_features(self):
        return len(self.features)
    
    def build_reduced_dataset(self,min_row,max_row,min_col,max_col,n_samples):
    	
    	table_reduced = "srp_reduced"
    	#drop old table
    	cursor = self.cnx.cursor()
        cursor.execute("DROP table " + table_reduced)
        self.cnx.commit()
        cursor.execute("CREATE TABLE " + table_reduced + " AS SELECT * FROM " + self.table + " WHERE 1=2")
        cursor.execute("ALTER TABLE " + table_reduced + " ADD COLUMN discretized_speed int")
        cursor.execute("ALTER TABLE " + table_reduced + " ADD COLUMN discretized_course int")
        cursor.execute("CREATE INDEX discretized_speed ON " + table_reduced + "(discretized_speed)")
        cursor.execute("CREATE INDEX discretized_course ON " + table_reduced + "(discretized_course)")
        self.cnx.commit()
        
    	#condition = "row between " + str(min_row) + " and " + str(max_row) + " and col between " + str(min_col) + " and " + str(max_col) + " and record_id < 1000 ORDER BY random() LIMIT 1"
    	
    	fields = ""
    	for i in range(0, len(self.lf_geom)):
    		fields = fields + self.lf_geom[i] + ", "
    	fields = fields[0:len(fields)-2]
    	
    	# extract n_samples for each class
    	for row in range(min_row,max_row+1):
    		for col in range(min_col,max_col+1):
    			condition = "row =" + str(row) + " and col =" + str(col) + " AND next_status_30 != -1 AND next_status_45 != -1 AND next_status_60 != -1 ORDER BY random() LIMIT " + str(n_samples)
    			cursor = self.select(self.table, self.lf_geom, condition)
    			records = self.cursor_to_list(cursor,self.lf_geom)
    			# store records in the table
    			for i in range(0, len(records)):
    				record = []
    				for field in self.lf_geom:
    					record.append(records[i][field])
    				self.insert(table_reduced,fields,record)
    
    def close_cnx(self):
        self.cnx.close()  
        
    def get_discretized_speed(self,speed):
    	# speed class
    	sc = 0 # slow - speed between 0.5 and 3
    	if speed > 3 and speed <= 14:
    		sc = 1 # medium
    	elif speed > 14 and speed <= 23:
    		sc = 2 # high
    	elif speed > 23 and speed <= 99:
    		sc = 3 # very high
    	elif speed > 99:
    		sc = 4 # exception
    	return sc 
    	
    def get_discretized_course(self, course):
    	# course class
    	cc = 0 # nord 337.5 - 22.5
    	if course > 22.5 and course <= 67.5:
    		cc = 1
    	elif course > 67.5 and course <= 112.5:
    		cc = 2
    	elif course > 112.5 and course <= 157.5:
    		cc = 3
    	elif course > 157.5 and course <= 202.5:
    		cc = 4
    	elif course > 202.5 and course <= 247.5:
    		cc = 5
    	elif course > 247.5 and course <= 292.5:
    		cc = 6
    	elif course > 292.5 and course <= 337.5:
    		cc = 7
    	return cc
    	
    def discretize_speed(self,table, sc, smin, smax):
    	
    	set = "discretized_speed = " + str(sc) + ""
        where = "speed > " + str(smin) + " and speed <= " + str(smax)
        self.update(table, set, where)
        
    def discretize_course(self,table, cc, cmin, cmax):
    	set = "discretized_course = " + str(cc) + ""
        where = "course > " + str(cmin) + " and course <= " + str(cmax)
        if cc == 0:
    		where = "(course >= 0 and course <= 22.5) or (course > 337.5 and course <= 360)"
        self.update(table, set, where)
    
    def discretize(self,table):
    	self.discretize_speed(table, 0, 0.49, 3)
    	self.discretize_speed(table, 1, 3, 14)
    	self.discretize_speed(table, 2, 14, 23)
    	self.discretize_speed(table, 3, 23, 99)
    	# discretize course
    	self.discretize_course(table, 0, 0, 0)
    	self.discretize_course(table, 1, 22.5, 67.5)
    	self.discretize_course(table, 2, 67.5, 112.5)
    	self.discretize_course(table, 3, 112.5, 157.5)
    	self.discretize_course(table, 4, 157.5, 202.5)
    	self.discretize_course(table, 5, 202.5, 247.5)
    	self.discretize_course(table, 6, 247.5, 292.5)
    	self.discretize_course(table, 7, 247.5, 337.5)
    	
    

