<?php
header("Access-Control-Allow-Origin: *");
include 'connection.php';


$data = json_decode( file_get_contents( 'php://input' ), true );


$pst=json_encode($data);
$fp = fopen('purchase.txt', 'w');
fwrite($fp, $pst);
fclose($fp);

$email = $data['contact']['email'];
$name = $data['contact']['first_name'].' '.$data['contact']['last_name'];

$sql = "INSERT INTO `users` ( `name`, `email`, `email_verified_at`, `password`, `remember_token`, `created_at`, `updated_at`, `is_admin`, `active`) VALUES ('$name', '$email',now(), '$2y$10$v/3bM6bSI/1iK6XIagjeCO7MUst0NBLxKOM1ue7vcQKCwdFJZ8b.O', NULL,now(),now(), '0', '1')";



$fp = fopen('latquery.txt', 'w');
fwrite($fp, $sql);
fclose($fp);

if ($conn->query($sql) === TRUE) {
               $return['ok'] = true;
                echo json_encode($return);
        } else {
           $return['ok'] = false;
                echo json_encode($return);
 }

  ?>
