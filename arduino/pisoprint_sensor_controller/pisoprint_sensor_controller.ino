/*
  PisoPrint Sensor Controller for Arduino Uno R3
  
  This sketch interfaces with:
  - HX711 load cell amplifier for paper weight measurement
  - 4 non-contact water level sensors for ink levels
  
  Communication with the Raspberry Pi/PC host is done via Serial.
*/

#include "HX711.h"

// HX711 load cell pins
#define LOADCELL_DOUT_PIN 4
#define LOADCELL_SCK_PIN 5

// Non-contact water level sensor pins (analog)
#define INK_BLACK_PIN A0
#define INK_CYAN_PIN A1
#define INK_MAGENTA_PIN A2
#define INK_YELLOW_PIN A3

// Threshold for ink level detection
#define INK_THRESHOLD 500  // Analog reading threshold (0-1023)

// HX711 instance
HX711 scale;

// Calibration values
float calibration_factor = -467; // Default calibration factor
float empty_weight = 50.0;       // Weight of empty paper tray in grams
float full_weight = 350.0;       // Weight of full tray in grams

// Buffer for incoming commands
String inputString = "";
boolean stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  inputString.reserve(50);
  
  // Initialize HX711 scale
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(calibration_factor);
  scale.tare();  // Reset scale to 0
  
  // Initialize analog pins for ink sensors
  pinMode(INK_BLACK_PIN, INPUT);
  pinMode(INK_CYAN_PIN, INPUT);
  pinMode(INK_MAGENTA_PIN, INPUT);
  pinMode(INK_YELLOW_PIN, INPUT);
  
  // Send ready message
  delay(1000);
  Serial.println("READY");
}

void loop() {
  // Process any incoming commands
  if (stringComplete) {
    processCommand(inputString);
    // Clear the string for next command
    inputString = "";
    stringComplete = false;
  }
  
  // Check for serial input
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

void processCommand(String command) {
  command.trim();
  
  // Test command to check connectivity
  if (command == "TEST") {
    Serial.println("READY");
  }
  
  // Read paper weight from HX711
  else if (command == "READ_WEIGHT") {
    float weight = scale.get_units(5); // Average of 5 readings
    Serial.print("WEIGHT:");
    Serial.println(weight, 2);
  }
  
  // Read ink levels (binary values)
  else if (command == "READ_INK_BLACK") {
    int value = analogRead(INK_BLACK_PIN);
    Serial.print("INK_BLACK:");
    Serial.println(value > INK_THRESHOLD ? "HIGH" : "LOW");
  }
  else if (command == "READ_INK_CYAN") {
    int value = analogRead(INK_CYAN_PIN);
    Serial.print("INK_CYAN:");
    Serial.println(value > INK_THRESHOLD ? "HIGH" : "LOW");
  }
  else if (command == "READ_INK_MAGENTA") {
    int value = analogRead(INK_MAGENTA_PIN);
    Serial.print("INK_MAGENTA:");
    Serial.println(value > INK_THRESHOLD ? "HIGH" : "LOW");
  }
  else if (command == "READ_INK_YELLOW") {
    int value = analogRead(INK_YELLOW_PIN);
    Serial.print("INK_YELLOW:");
    Serial.println(value > INK_THRESHOLD ? "HIGH" : "LOW");
  }
  
  // Calibration commands
  else if (command.startsWith("CALIBRATE_WEIGHT:")) {
    String weightStr = command.substring(16);
    float knownWeight = weightStr.toFloat();
    if (knownWeight > 0) {
      // Get the raw value
      long rawValue = scale.read_average(10);
      // Calculate new calibration factor
      calibration_factor = rawValue / knownWeight;
      // Set the new scale
      scale.set_scale(calibration_factor);
      
      Serial.print("CALIBRATION_FACTOR:");
      Serial.println(calibration_factor, 4);
    } else {
      Serial.println("ERROR:Invalid weight value");
    }
  }
  else if (command.startsWith("SET_EMPTY_WEIGHT:")) {
    String weightStr = command.substring(17);
    empty_weight = weightStr.toFloat();
    Serial.print("EMPTY_WEIGHT_SET:");
    Serial.println(empty_weight, 2);
  }
  else if (command.startsWith("SET_FULL_WEIGHT:")) {
    String weightStr = command.substring(16);
    full_weight = weightStr.toFloat();
    Serial.print("FULL_WEIGHT_SET:");
    Serial.println(full_weight, 2);
  }
  else if (command == "TARE") {
    scale.tare();  // Reset scale to 0
    Serial.println("TARE_COMPLETE");
  }
  else {
    Serial.print("ERROR:Unknown command: ");
    Serial.println(command);
  }
} 