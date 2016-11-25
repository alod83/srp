# This script implements functions to parse file config.ini

from ConfigParser import ConfigParser

def init_config():
    config = ConfigParser()
    config.read("../config.ini")
    return config

# Generic function to retrieve parameters
def get_param(section, list):
    config = init_config()
    param = {}
    for i in list:
        param[i] = config.get(section, i)
    return param

# This function parses the MySQL section
def get_mysql():
    return get_param("SQL", {'user', 'password', 'db', 'table'})

# This function parses the Grid section
def get_grid():
    return get_param("Grid", {'cx', 'cy'})

# This fucntion parses the training and test sections
# type must be TrainingSet or TestSet
def get_training_set():
    return get_param("TrainingSet", {'percentage', 'prediction_step'})

def get_features():
    return get_param("Features", {'small_ship_length', 'small_ship_width', 'big_ship_length','big_ship_width'})

