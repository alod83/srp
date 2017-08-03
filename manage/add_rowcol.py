import os
import sys
config_path = "../knn/utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI
from geo import get_position_in_grid


api = MyAPI()
list = api.get_row_col_from_table(condition="record_id >= 600000 and record_id < 900000")
gp =  api.get_grid_parameters()
for i in range(0,len(list)):
    record_id = list[i]['record_id']
    row = float(list[i]['row']) # lng
    col = float(list[i]['col']) # lat
    row_col = str(int(row)) + "_" + str(int(col))
    api.set_rowcol(record_id, row_col)
    