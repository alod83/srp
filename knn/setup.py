import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI

api = MyAPI()
api.build_datasets() 