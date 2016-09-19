# This script contains a collection of functions


# This function runs a mysql query
def myquery(cnx,query):
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    return cursor