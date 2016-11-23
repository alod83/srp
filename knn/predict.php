<?php 

$python_env = "/Library/Frameworks/Python.framework/Versions/2.7/bin/python";
header('Content-Type: application/json');

if(isset($_GET['latitude']) && isset($_GET['longitude']) && isset($_GET['cog']) && isset($_GET['sog']) && $_GET['precision_step'])
{
	$lat = $_GET['latitude'];
	$lng = $_GET['longitude'];
	$cog = $_GET['cog'];
	$sog = $_GET['sog'];
	$p = $_GET['precision_step'];
	$output = "";
	exec("$python_env predict.py -l $lat -n $lng -c $cog -s $sog -p $p", $output);
	echo $output[0];
}
else 
	echo "Parameters: latitude, longitude, sog, cog, precision_step";
?>