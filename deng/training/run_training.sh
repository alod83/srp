#!/bin/sh

# This script runs the first part of the SRP algorithm

echo "Run Training Module"
# split the area in a grid and map each vessel in a cell in the grid
# map timestamps to the associated table
echo "GRID-TIMESTAMP"
python grid-timestamp.py
# map speed over ground (sog) and course over ground (cog) to their associated tables
echo "SOG-COG"
python sog-cog.py
# build patterns
echo "PATTERN"
python pattern.py
# build itemsets
echo "ITEMSET"
python itemset.py
# build confidence
echo "MBA"
python mba.py
echo "End Training Module"
