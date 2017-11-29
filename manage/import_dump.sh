#!/bin/bash

echo "* * * * * Import Dump * * * * *"

user="postgres"
export PGPASSWORD=''
db_name=""
db_link=""

# TODO read from url, use wget
usage() { echo "Usage: $0 [-f <path to file>][-w]" 1>&2; exit 1; }

b_wget=false
while getopts "f:w" o; do
    case "${o}" in
        f)
            file=${OPTARG}
            ;;
        w)  b_wget=true
            ;;
        *)
            usage
            ;;
    esac
done

echo $b_wget
shift $((OPTIND-1))

if [ -z "${file}" ] && [ "$b_wget" = false ]; then
    usage
fi

if [ "$b_wget" = true ] 
then
    echo "downloading dump"
    #wget $db_link
    #unzip osiris.zip 
    file="var/lib/pgsql/backup/osiris.dump"
    echo "done"
fi

echo "Importing dump in the $db_name database"
psql -U postgres<<EOF
\connect $db_name
DROP TABLE ais_data;
EOF
pg_restore -U postgres -d $db_name -t ais_data $file
echo "Done"

echo "Getting last datetime"
last_time=$(psql -U postgres -q -t -d $db_name <<EOF
SELECT max(date_time) FROM ais_data_clean;
EOF
)
echo "last_time=$last_time"

echo "Removing duplicates"
psql -U postgres <<EOF
\connect $db_name
INSERT INTO ais_data_clean SELECT DISTINCT date_time,mmsi,course,speed,heading,imo,ship_name,callsign,ship_type,a,b,c,d,draught,destination,eta,navigation_status,geom FROM ais_data WHERE date_time > '$last_time';
INSERT INTO srp_dataset SELECT DISTINCT date_time,mmsi,course,speed,heading,imo,ship_name,callsign,ship_type,a,b,c,d,draught,destination,eta,navigation_status,geom FROM ais_data_clean WHERE date_time > '$last_time' AND heading >= 0 and heading <= 359 and speed >= 0.5 and speed <= 60;

EOF

rm $file
echo "Done"

echo "Starting setup"
end_time=$(psql -U postgres -q -t -d $db_name <<EOF
SELECT max(date_time) FROM srp_dataset;
EOF
)
python /home/angelica/Git/osiris/knn/setup.py -s $last_time -e $end_time -b 1
echo "Done"

echo "Running training"
nr=$(psql -U postgres -q -t -d $db_name <<EOF
SELECT max(record_id) FROM srp_dataset;
EOF
)

echo "KNN"
python /home/angelica/Git/osiris/knn/train.py -a knn -n $nr 
cp /home/angelica/Git/osiris/knn/data/*knn* /var/www/html/srp/data/
echo "Done"

echo "Getting classes"
python /home/angelica/Git/osiris/knn/get_classes.py -n $nr
cp /home/angelica/Git/osiris/knn/classes.csv /var/www/html/srp_viewer/dump/
echo "Done"

