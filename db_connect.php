<?php
// Make sure your database connection is properly configured
try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    // Set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    // Log the error instead of displaying it
    error_log("Connection failed: " . $e->getMessage());
    // Show a user-friendly message
    die("Database connection error. Please contact the administrator.");
} 