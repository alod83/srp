#!/bin/sh

echo "* * * * * WELCOME TO SHIP ROUTE PREDICTION ALGORITHM * * * * *"
echo "Please look at config.ini for configuration options"

cd discretize
sh run_discretize.sh
cd ..
