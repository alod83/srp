<?php 

$python_env = "/usr/bin/python";
header('Content-Type: application/json');

if(isset($_GET['latitude']) && 
		isset($_GET['longitude']) && 
		isset($_GET['heading']) && 
		isset($_GET['sog']) && 
		isset($_GET['precision_step']) &&
		isset($_GET['basic_class']))
{
	$lat = $_GET['latitude'];
	$lng = $_GET['longitude'];
	$heading = $_GET['heading'];
	$sog = $_GET['sog'];
	$p = $_GET['precision_step'];
	$bc = $_GET['basic_class'];
	$output = "";
	exec("$python_env predict.py -l $lat -n $lng -c $heading -s $sog -b $bc -p $p", $output);
	echo $output[0];
}
else 
	echo "Parameters: latitude, longitude, sog, heading, basic_class, precision_step";
?>
