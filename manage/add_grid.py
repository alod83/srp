import os
import sys
config_path = "../knn/utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI
from geo import get_position_in_grid


api = MyAPI()
list = api.get_all_from_table(condition="record_id >= 1500000 and record_id <= 2000000")
gp =  api.get_grid_parameters()
for i in range(0,len(list)):
    record_id = list[i]['record_id']
    lng = float(list[i]['ST_X (ST_Transform (geom, 4326))']) # lng
    lat = float(list[i]['ST_Y (ST_Transform (geom, 4326))']) # lat
    col, row = get_position_in_grid(lng,lat,float(gp['cx']),float(gp['cy']))
    api.set_grid_position(record_id, int(row), int(col))
    