<?php 
/*
 * This script retrieves some statistics about vessels
 */

header('Content-Type: application/json');

if(!isset($_GET['locality']) || !isset($_GET['type']))
	echo json_encode(array('status' => 'error', 'details' => 'missing parameters. Please specify type and locality'));
else 
{
	$locality = $_GET['locality'];
	$type = ucfirst(strtolower($_GET['type']));
	
	include('../utilities/config.php'); // configuration file, not included in Git
	
	
	$q = "";
	switch($type)
	{
		case 'Type':
		case 'Flag':
			$q = "	SELECT $type, COUNT($type) AS Tot
					FROM ".$locality."_Info
					GROUP BY  $type
					ORDER BY  `Tot` DESC ";
			break;
		case 'Speed':
		case 'Course':
			$field = strtolower($type);
			$q = "	SELECT value AS $type, count(value) AS Tot
					FROM ".$locality."_$type, $type
					WHERE $type.id = ".$locality."_$type.".$field."_id
					GROUP BY value";
			break;
	}
	
	
	$arg = array('type' => $type);
	$return = mysqlquery($conn,$q,$arg, function ($aRow, $arg, &$return)
	{
		$type = $arg['type'];
		$return[] = array($type => $aRow[$type], 'Total' =>intval($aRow['Tot']));
			
	});
	
	echo json_encode($return);
}
?>