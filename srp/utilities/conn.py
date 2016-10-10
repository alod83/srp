import mysql.connector as mysql
# load mysql parameters
from config import get_mysql

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
    
    def select(self,table, fields, condition):
        query = "SELECT "
        for field in fields:
            query = query + field + ", "
        query = query[:-2] + " FROM " + table + " WHERE " + condition
        print query
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
        cursor = self.select(self.locality, self.lf, "1 LIMIT 3")
        return self.cursor_to_list(cursor,self.lf)
    
    def get_min_max_from_type(self,type):
        fields = ['id','min','max']
        cursor = self.select(type, fields, "1 LIMIT 3")
        return self.cursor_to_list(cursor,fields)
    
    def get_type_ranges_from_locality(self,type,min,max):
        type = type.upper()
        fields = ['MMSI', type]
        data = {'type' : type, 'min' : min, 'max': max}
        condition = "%(type)s >= '%(min)s' AND %(type)s < '%(max)s'" % (data)
        cursor = self.select(self.locality,fields, condition + " LIMIT 3")
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
        
    def set_timestamp(self,values):
        self.insert("Timestamp", "vessel_id, year, month, day,sh,eh", values)
    
    def set_grid(self,values):
        self.insert("Grid", "vessel_id, row, col, timestamp,name", values)
        
    def set_type(self,values,type):
         fields = "vessel_id,%(type)s_id" %({'type' : type})
         self.insert(type, fields,values)
        
        