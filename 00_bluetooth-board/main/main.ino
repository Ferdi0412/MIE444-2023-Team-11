/*Note:

This is intended for use with the ESP32 board. To upload the code, you must press the "Boot" button while uploading...
(On the actual board, the "B" is rubbed off, so it looks like "oot")
Otherwise you will have "uploading error: exit status 2"

Also note that for some reason, compiling and uploading to the ESP32 is MUCH slower than to a regular arduino board.

*/

// Setup using ESP32 Dev Module...

// Quick tutorial for bluetooth on esp32: https://randomnerdtutorials.com/esp32-bluetooth-classic-arduino-ide/
#include "BluetoothSerial.h"

// Tutorial on getting address: https://www.youtube.com/watch?v=fxvoNpiqipQ
#include "esp_bt_device.h"

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(9600); // For monitor in Arduino IDE
  
  SerialBT.begin("MIE444-Group-11");

  Serial.println("Now pairable...");

  // Print bluetooth adress
  Serial.println("Bluetooth address:");

  const uint8_t* address = esp_bt_dev_get_address();
  for ( int i = 0; i < 6; i++ ) {
    char str[3];
    sprintf(str, "%02X", (int) address[i]);
    Serial.print(str);
    if ( i < 5 )
      Serial.print(":");
  }
  Serial.print("/n");
}

void loop() {
  // If SerialBT.available() -> Message received
  if ( SerialBT.available() ) {
    // Send to Arduino monitor...
    Serial.write(SerialBT.read());
  }
}
