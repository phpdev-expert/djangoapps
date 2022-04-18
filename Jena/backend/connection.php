<?php
ini_set('display_startup_errors',1);
ini_set('display_errors',1);
error_reporting(-1);
$servername = "localhost";
$serverusername = "root";
$serverpassword = "admin1123";
$dbname = 'hellotags';
// Create connection
$conn = new mysqli($servername, $serverusername, $serverpassword,$dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
