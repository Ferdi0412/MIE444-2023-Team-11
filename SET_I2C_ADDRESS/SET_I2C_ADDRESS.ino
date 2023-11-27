#include <Wire.h>

#define XSHUT_PIN 6  // Replace with the actual GPIO pin connected to XSHUT

void setup() {
  Serial.begin(9600);

  pinMode(XSHUT_PIN, OUTPUT);
  digitalWrite(XSHUT_PIN, LOW);  // Start by pulling XSHUT low

  Wire.begin();  // Initialize I2C communication

  delay(10);  // Wait for the sensor to power up

  // Release XSHUT to allow the sensor to use the default I2C address
  digitalWrite(XSHUT_PIN, HIGH);

  delay(10);  // Wait for the sensor to exit shutdown mode

  // Now you can communicate with the sensor using the default I2C address
}

void loop() {
  // Your code here
  if ( Serial.available() ) {
    switch ( Serial.read() ) {
      case 'C' : {
        changeI2CAddress();
        break;
      }

      case 'S' : {
        scanI2CDevices();
        break;
      }
    }
  }
}




void scanI2CDevices() {
  Serial.println("Scanning...");

  for (byte i = 8; i < 127; i++) {
    Wire.beginTransmission(i);
    byte error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Found device at address 0x");
      if (i < 16) {
        Serial.print("0");
      }
      Serial.println(i, HEX);
    }
  }

  Serial.println("Scan complete.");
}




void changeI2CAddress() {
  // Write the new I2C address (0x30 in this example) to the register
  Wire.beginTransmission(0x29);  // Default I2C address
  Wire.write(0x8A);  // Register address for changing the I2C address
  Wire.write(0x32);  // New I2C address
  Wire.endTransmission();

  delay(10);  // Wait for the sensor to process the new address

  // Power cycle the sensor by pulling XSHUT low and then releasing it
  digitalWrite(XSHUT_PIN, LOW);
  delay(10);
  digitalWrite(XSHUT_PIN, HIGH);
}
