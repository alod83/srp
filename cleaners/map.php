<?php

/* This script maps vessels to speed/course
 * 
 */

include('../utilities/config.php'); // configuration file, not included in Git

$table = "Speed"; // Speed or Course
$locality = "Malta";

// get the list of speeds
$q = "SELECT * FROM $table";
$arg = array('conn'=> $conn, 'table' => $table, 'locality' => $locality);
mysqlquery($conn,$q,$arg, function ($aRow, $arg){
	// for each speed search which vessels fall in the range
	$min = $aRow['min'];
	$max = $aRow['max'];
	$conn = $arg['conn'];
	$table = $arg['table'];
	$locality = $arg['locality'];
	
	$arg = array('conn' => $conn, 'id' => $aRow['id'], 'table' => $table,'locality' => $locality);
	$field = strtoupper($table);
	$q = "SELECT MMSI, $field FROM $locality WHERE $field >= '$min' AND $field < '$max'";

	mysqlquery($conn,$q,$arg, function ($aRow, $arg)
	{
		$conn = $arg['conn'];
		$locality = $arg['locality'];
		
		$id = $arg['id'];
		$table = $arg['table'];
		$field = strtolower($table);
		$vessel_id = $aRow['MMSI'];
		echo $vessel_id."\n";
		mysqli_query($conn, "INSERT INTO ".$locality."_$table(vessel_id,".$field."_id) VALUES('$vessel_id', '$id')");
		
	});
});

mysqli_close($conn);
?>