import mysql.connector as mysql
# load mysql parameters
from config import get_mysql

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
    
    training_condition = "1 LIMIT 10"
    
    # init object by opening a MySQL connection
    def __init__(self):
        mp = get_mysql()
        self.cnx = mysql.connect(user=mp['user'], password=mp['password'],database=mp['db'])
        self.locality = mp['locality']
    
    def select(self,table, fields, condition):
        query = "SELECT "
        for field in fields:
            query = query + field + ", "
        query = query[:-2] + " FROM " + table + " WHERE " + condition
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
        cursor = self.select(type, fields, self.training_condition)
        return self.cursor_to_list(cursor,fields)
    
    def get_type_ranges_from_locality(self,type,min,max):
        type = type.upper()
        fields = ['MMSI', type]
        data = {'type' : type, 'min' : min, 'max': max}
        condition = "%(type)s >= '%(min)s' AND %(type)s < '%(max)s'" % (data)
        cursor = self.select(self.locality,fields, condition + self.training_condition)
        return self.cursor_to_list(cursor,fields)
    
    def get_pattern(self):
        fields = ['pattern']
        cursor = self.select(self.locality + "_Pattern", fields,"1")
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
        print query
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
        print vs
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
        print query
        cursor = self.cnx.cursor(buffered=True)
        cursor.execute(query)
        self.cnx.commit()
        count = cursor.rowcount
        cursor.close()
        return count
     
    def close_cnx(self):
        self.cnx.close()   
        