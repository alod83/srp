<?php 

/*
 * This script retrieves information about vessels from vesselfinder.com
 * Retrieved properties are in the following order:
 * - Last report
 * - Ship type
 * - Flag
 * - Destination
 * - ETA
 * - Lat/Lon
 * - Course/Speed
 * - Current Draught
 * - Callsign
 * - IMO/MMSI
 * - Built
 */

// These scripts are contained in the repository templates (in a separate Git)
include('../templates/php/utilities/remote.php');
include('../templates/php/utilities/utilities.php');
include('utilities/config.php'); // configuration file, not included in Git

$basic_url = "https://www.vesselfinder.com/vessels/";

$nXPATH = "//div[@class=\"small-5 columns name\"]/span";
$vXPATH = "//span[@class=\"small-7 columns value\"]";

// array of values to be excluded
$ev = array("Premium users only");
$en = array("Last report:","Builder","Place of build","Deadweight","Owner","Manager");

//$conn = mysqlconnect("root", NULL,"OSIRIS");
$query = "SELECT DISTINCT(MMSI), NAME FROM Bosforo WHERE NAME != ''";
$qr = mysqli_query($conn, $query);
if($qr != false && mysqli_num_rows($qr) > 0)
	while($row = mysqli_fetch_assoc($qr))
	{
		$name = str_replace(" ","-",preg_replace('/\s+/', ' ',str_replace('-'," ",str_replace(array('/',"'","..."),"",trim($row['NAME'])))));
		//$imo = $row['IMO'];
		$mmsi = $row['MMSI'];
		$vessel = "$name-IMO-0-MMSI-$mmsi";
		$vessel_url = $basic_url.$vessel;
		
		echo $vessel_url."\n";
		
		$response = connect_curl($vessel_url);
		
		$dom = connect_DOM($response['response'], false, "HTML");
		
		// retrieve properties names
		$nodes_list = XPATH($dom,$nXPATH);
		$pn = get_nv_from_nl($nodes_list,$en);
		
		// retrieve properties values
		$nodes_list = XPATH($dom,$vXPATH);
		$pv = get_nv_from_nl($nodes_list,$ev);
		
		if(!empty($pn) && !empty($pv))
		{
			// strings of properties names and values
			$spn = "";
			$spv = "";
			for($i = 0; $i < count($pv); $i++)
			{
				$spn .= "`".$pn[$i]."`,";
				$spv .= "'".$pv[$i]."',";
			}
			// remove the last comma
			$spn = substr($spn,0, strlen($spn)-1);
			$spv = substr($spv,0, strlen($spv)-1);
			
			$iq = "INSERT INTO Bosforo_Info(`MMSI`,$spn) VALUES ('$mmsi',$spv)";
			mysqli_query($conn,$iq);
		}
	}
mysqli_close($conn);

?>