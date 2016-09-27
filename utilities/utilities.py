# This script contains a collection of functions


# This function runs a mysql query
def myquery(cnx,query,buffered=True):
    cursor = cnx.cursor(buffered)
    cursor.execute(query)
    return cursor