<?php
header("Access-Control-Allow-Origin: *");
include 'connection.php';




$data = json_decode( file_get_contents( 'php://input' ), true );


$pst=json_encode($data);
$fp = fopen('contact.txt', 'w');
fwrite($fp, $pst);
fclose($fp);

$email = $data['purchase']['contact']['email'];


$sql = "INSERT INTO users VALUES(NULL, '$email', '1', '0', CURRENT_TIMESTAMP)";
if ($conn->query($sql) === TRUE) {
               $return['ok'] = true;
                echo json_encode($return);
        } else {
           $return['ok'] = false;
                echo json_encode($return);
 }

  ?>
