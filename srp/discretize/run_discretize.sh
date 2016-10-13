#!/bin/sh

# This script runs the first part of the SRP algorithm

echo "Run Discretization Module"
# split the area in a grid and map each vessel in a cell in the grid
# map timestamps to the associated table
python grid-timestamp.py
# map speed over ground (sog) and course over ground (cog) to their associated tables
python sog-cog.py
# build patterns
python pattern.py
echo "End Discretization Module"
