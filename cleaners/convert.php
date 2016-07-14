<?php

/*
 * This script converts all the columns of a table from string to decimal
 */

include('../utilities/config.php'); // configuration file, not included in Git

$q = "SELECT MMSI, SPEED, COURSE from Malta";
$arg = array('conn'=> $conn);
mysqlquery($conn,$q,$arg, function ($aRow, $arg){
	
	$conn = $arg['conn'];
	$speed = floatval(str_replace(",",".",$aRow['SPEED']));
	$course = floatval(str_replace(",",".",$aRow['COURSE']));
	$id = $aRow['ID'];
	
	mysqli_query($conn, "UPDATE Malta SET SPEEDD = '$speed', COURSED = '$course' WHERE ID = '$id'");
	
});
?>