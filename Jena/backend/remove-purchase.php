<?php
header("Access-Control-Allow-Origin: *");
include 'connection.php';



$data = json_decode( file_get_contents( 'php://input' ), true );
$email = $data['purchase']['contact']['email'];


$sql = "delete from  users where email='$email'";
if ($conn->query($sql) === TRUE) {
               $return['ok'] = true;
                echo json_encode($return);
        } else {
           $return['ok'] = false;
                echo json_encode($return);
 }

  ?>
