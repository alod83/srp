#!/bin/bash

echo $(date)
start_index=600000
#ntot=18510501
#ntot=8394637
ntot=1000000
# number of processes
np=5
nr=$(((ntot-start_index) / np))
echo $nr
#end_index=$((start_index+nr))
end_index=$((start_index+100000))
for(( i=1; i<=$np; i++ ))
	do
		if [ "$end_index" -gt "$ntot" ]; then
			end_index=$ntot
		fi
		echo "$i start index: $start_index end_index $end_index"
		python setup.py -s $start_index -b 1 -e $end_index &
		#start_index=$((end_index+1))
		start_index=$((end_index+19000))
		#end_index=$(((i+1)*(nr)))
		end_index=$((start_index+100000))
	done
echo $(date)