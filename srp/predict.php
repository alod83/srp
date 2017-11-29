<?php 

$python_env = "/usr/bin/python";
header('Content-Type: application/json');

if(isset($_GET['latitude']) && 
		isset($_GET['longitude']) && 
		isset($_GET['heading']) && 
		isset($_GET['sog']) && 
		isset($_GET['basic_class']))
{
	$lat = $_GET['latitude'];
	$lng = $_GET['longitude'];
	$heading = $_GET['heading'];
	$sog = $_GET['sog'];
	$bc = $_GET['basic_class'];
	$algorithm = isset($_GET['algorithm']) ? $_GET['algorithm'] : 'knn';
	$output = "";
	exec("$python_env predict.py -a $algorithm features -l $lat -n $lng -c $heading -s $sog -b $bc", $output);
	echo $output[0];
}
else if (isset($_GET['record_id']))
{
	$algorithm = isset($_GET['algorithm']) ? $_GET['algorithm'] : 'knn';
	$output = "";
	$record_id = $_GET['record_id'];
	exec("$python_env predict.py -a $algorithm record_id -r $record_id", $output);
	echo $output[0];
}
else
	echo "Parameters: latitude, longitude, sog, heading, basic_class, algorithm, record_id (optional, default is knn)";
?>
