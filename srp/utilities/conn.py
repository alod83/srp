import mysql.connector as mysql
# load mysql parameters
from config import get_mysql
from config import get_t_set

# TODO Remove limit 3 from queries.
class MyConn:
    
    lf = [
        'MMSI',
        'TIME',
        'TIMESTAMP',
        'LATITUDE',
        'LONGITUDE',
        'NAME',
        'SPEED',
        'COURSE'
    ]
    
    
    
    # init object by opening a MySQL connection
    def __init__(self):
        mp = get_mysql()
        self.cnx = mysql.connect(user=mp['user'], password=mp['password'],database=mp['db'])
        self.locality = mp['locality']
        trs = get_t_set("TrainingSet")
        self.training_condition = "NAME IN (" + trs['vessels'] + ")"
    
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
        while row is not None:
            result.insert(j, dict())
            for i in range(0,len(fields)):
                result[j][fields[i]] = row[i] 
            j = j + 1
            row = cursor.fetchone()
        return result
    
    # get all fields from table 
    def get_all_from_locality(self):
        cursor = self.select(self.locality, self.lf, self.training_condition)
        return self.cursor_to_list(cursor,self.lf)
    
    def get_min_max_from_type(self,type):
        fields = ['value','min','max']
        cursor = self.select(type, fields, "1")
        return self.cursor_to_list(cursor,fields)
    
    def get_type_ranges_from_locality(self,type,min,max):
        type = type.upper()
        fields = ['MMSI', type]
        data = {'type' : type, 'min' : min, 'max': max}
        condition = "%(type)s >= '%(min)s' AND %(type)s < '%(max)s' AND " % (data)
        cursor = self.select(self.locality,fields, condition + self.training_condition)
        return self.cursor_to_list(cursor,fields)
    
    def get_pattern(self,distinct=None):
        fields = ['pattern','name','pattern_id']
        if distinct is not None:
            fields = ['distinct pattern_id']
        cursor = self.select(self.locality + "_Pattern", fields,"1 ORDER BY timestamp ASC")
        return self.cursor_to_list(cursor,fields)
    
    
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
    
    def set_pattern_table(self,fields,values):
        table = "Pattern"
        where = "vessel_id = '" + str(values[0]) + "'"
        fn = fields.split(",")
        vs = ""
        for i in range(0,len(values)-1):
            vs = vs + fn[i] + "='" + str(values[i+1]) + "',"
        #remove last comma
        vs = vs[:-1]
        affected_rows = self.update(table, vs,where)
        if affected_rows == 0:
            self.insert(table, "vessel_id," + fields, values)    
            
    def set_timestamp(self,values):
        fields = "year,month,day,sh,eh"
        self.set_pattern_table(fields,values)
    
    def set_grid(self,values):
        fields = "row, col, timestamp,name"
        self.set_pattern_table(fields,values)
        
    def set_type(self,values,type):
         fields = "%(type)s_id" %({'type' : type})
         self.set_pattern_table(fields,values)
    
    def set_pattern_id(self):
        table = "Pattern"
        set = "pattern = CONCAT_WS('_', row, col,speed_id,course_id,sh)"
        self.update(table, set)
        
    def set_itemset(self,values):
        table = "Itemset"
        fields = "itemset_id,pattern_id"
        self.insert(table, fields, values)
        
    def set_confidence(self,values):
        table = "Confidence"
        fields = "ant,cons,confidence"
        self.insert(table,fields,values)
    
             
    def update(self,table,set,where=None):
        if where == None:
            where = "1"
        data = {
            'locality'  : self.locality,
            'table'     : table,
            'set'       : set,
            'where'     : where
        }
        
        query = "UPDATE %(locality)s_%(table)s SET %(set)s WHERE %(where)s" %(data)
        cursor = self.cnx.cursor(buffered=True)
        cursor.execute(query)
        self.cnx.commit()
        count = cursor.rowcount
        cursor.close()
        return count
    
    def count_items(self,ant,cons=None):
        fields = ["COUNT(pattern_id)"]
        condition = "pattern_id = '" + str(ant) + "'"
        if cons is not None:
            condition = condition + " AND itemset_id IN (SELECT itemset_id FROM " + self.locality + "_Itemset WHERE pattern_id = '" + str(cons) + "' )"
        cursor = self.select(self.locality + "_Itemset", fields, condition)
        row = cursor.fetchone()
        return row[0]
        
     
    def close_cnx(self):
        self.cnx.close()   
        