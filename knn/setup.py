import os
import sys
config_path = "utilities/"
sys.path.append(os.path.abspath(config_path))
from MyAPI import MyAPI
import argparse

parser = argparse.ArgumentParser(description='Setup')
parser.add_argument('-s', '--start_index', help='start_index',type=int,required=False)
parser.add_argument('-e', '--end_index', help='end_index',type=int,required=False)
parser.add_argument('-b', '--burst', help='burst',type=int,required=False)

args = parser.parse_args()
api = MyAPI()
# take burst elements at time
burst = 50000
if args.burst is not None:
    burst = args.burst
    
# number of records. Calculated offline for performance reasons
nr = 18510501
if args.end_index is not None:
    nr = int(args.end_index)

start_index = 0 #180487
if args.start_index is not None:
    start_index = int(args.start_index)
    
end_index = start_index + burst
while end_index <= nr:
    api.build_datasets(extract_test=True,start_index=start_index,end_index=end_index,continue_from_previous_run=False)
    start_index = end_index + 1
    end_index = start_index + burst
    #if end_index > nr:
    #    end_index = nr
#api.build_datasets() 