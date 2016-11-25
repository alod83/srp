<?php 

$python_env = "/usr/bin/python";
header('Content-Type: application/json');

if(isset($_GET['latitude']) && 
		isset($_GET['longitude']) && 
		isset($_GET['cog']) && 
		isset($_GET['sog']) && 
		isset($_GET['precision_step']) &&
		isset($_GET['basic_class']))
{
	$lat = $_GET['latitude'];
	$lng = $_GET['longitude'];
	$cog = $_GET['cog'];
	$sog = $_GET['sog'];
	$p = $_GET['precision_step'];
	$bc = $_GET['basic_class'];
	$output = "";
	exec("$python_env predict.py -l $lat -n $lng -c $cog -s $sog -b $bc -p $p", $output);
	echo $output[0];
}
else 
	echo "Parameters: latitude, longitude, sog, cog, basic_class, precision_step";
?>
