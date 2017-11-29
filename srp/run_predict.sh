#!/bin/bash

# leggere da linea di comando la data e l'id
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
mydate="2017-10-16"
ID="prova"
while getopts "h?i:d:" opt; do
    case "$opt" in
    h|\?)
        echo "usage run_predict.sh -i folder_id -d folder_date"
        exit 0
        ;;
    i)  ID=$OPTARG
        ;;
    d)  mydate=$OPTARG
        ;;
    esac
done

declare -A modules

# correggere il percorso
data_dir="/home/angelica/Git/osiris/srp/"$mydate"/"$ID"/"
module_dir="/home/angelica/Git/osiris/srp/"

# TODO check whether my file .done exists in this case exit
#srp_done=$data_dir"SRP/SRP.done"
#if [ -f "$srp_done" ];
#then
#	echo "Data already processed"
#	exit 1
#fi

declare -a modules_name=("detection" "classification" "kinematic")
declare -A modules[detection]
modules[detection,name]="SD"
modules[detection,filepath]="SD/detection.csv"
declare modules[detection,fields]
modules[detection,fields,0]='SdI'
modules[detection,fields,1]='SClat'
modules[detection,fields,2]='SClon'
modules[detection,fields,3]='SL'
modules[detection,fields,4]='SW'
modules[detection,fields,5]='SH'


declare -A modules[classification]
modules[detection,classification]="SC"
modules[classification,filepath]="SC/classification.csv"
declare modules[classification,fields]
modules[classification,fields,0]='SdI'
modules[classification,fields,1]='SC'	# Ship class
modules[classification,fields,2]='ST'	# Ship type
modules[classification,fields,3]='SFL'	# Ship type
modules[classification,fields,4]='SFW'	# Ship type
modules[classification,fields,5]='HDAM'	# Ship type
modules[classification,fields,6]='SFH'	# Ship fine heading

declare -A modules[kinematic]
modules[kinematic,name]="SKE"
modules[kinematic,filepath]="SKE/kinematic.csv"
declare modules[kinematic,fields]
modules[kinematic,fields,0]='SdI'
modules[kinematic,fields,1]='SSA'		# Ship speed amplitude
modules[kinematic,fields,2]='SSO'


# TODO check whether the file .done exists

# Retrieve input data

declare -A features
declare SdI_list

for module in "${modules_name[@]}"
do
	filename=$data_dir${modules[$module,filepath]}
	
	count=1
	#echo $module
	while read line; do
		declare -A features
		# skip first line
		if [ $count -gt 1 ]
  		then
  			#arr_line=(${line//,/ })
  			IFS=',' read -r -a arr_line <<< $line
  			SdI=${arr_line[0]}
			
			if [ "$module" == "detection" ]; then
				declare -A features[$SdI]
				SdI_list+=($SdI)
			fi
  		
  			fields_array=${modules[$module,fields]}
  			for index in ${!arr_line[@]}; do
    			features[$SdI,${modules[$module,fields,$index]}]=${arr_line[$index]}
			done
			
  		fi
  		count=$((count + 1))
  		
	done <$filename
done

# prepare output file
output_file=$data_dir"SRP/route_prediction.json"
echo '{"type": "FeatureCollection", "features": [' > $output_file
# run predict for each SdI
for i in "${SdI_list[@]}"
do
	
  	#echo "{" >> $output_file
  	
  	lat=${features[$i,'SClat']}
  	lng=${features[$i,'SClon']}
  	sog=${features[$i,'SSA']}
  	cog=${features[$i,'SSO']}
  	bclass=${features[$i,'SC']}
  	use_sfh=false
  	if [ -z "$cog" ];
  	then
  		cog=${features[$i,'SFH']}
  		use_sfh=true
  	fi
  	if [ ! -z "$lat" ] && [ ! -z "$lng" ] && [ ! -z "$sog" ] && [ ! -z "$cog" ] && [ ! -z "$bclass" ]; then
  		#if [ "$i" != "${SdI_list[0]}" ];
  		#then
  		#	echo "," >> $output_file
  		#fi
  		python $module_dir/predict.py features -l $lat -n $lng -c $cog -s $sog -b $bclass -i ${features[$i,'SdI']} -o $output_file -f
		h_dam=${features[$i,'HDAM']}
		if [ "$h_dam" = "true" ] && [ "$use_sfh" = "true" ]; then
			cog=$(((cog + 180)%360))
			echo "," >> $output_file
			python $module_dir/predict.py features -l $lat -n $lng -c $cog -s $sog -b $bclass -i ${features[$i,'SdI']} -o $output_file -f 
		fi
	fi
	#echo "}" >> $output_file
	len=$((${#SdI_list[@]}))
	if [ "$i" -lt "$len" ]; then
		echo "," >> $output_file
	fi
done
echo "]}" >> $output_file

# create file .done
# TODO verificare che la cartella esista

#echo "" > $srp_done
  		