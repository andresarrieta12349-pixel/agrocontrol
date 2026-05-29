<?php
// Conexión básica a la base de datos de la finca
$servidor = "localhost";
$usuario = "root";
$clave = "";
$base_datos = "agrocontrol_db";

$conexion = mysqli_connect($servidor, $usuario, $clave, $base_datos);

if (!$conexion) {
    die("Error al conectar con la base de datos: " . mysqli_connect_error());
}
?>