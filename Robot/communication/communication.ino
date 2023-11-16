#include "BluetoothSerial.h"

#define LED 2

#define SensorSerial Serial

// Bluetooth Connection to communicate with Computer
BluetoothSerial ComputerBT;


void setup() {
  SensorSerial.begin(9600);

  // White-stripe (ie. the ESP32 board with white tape on it)...
  ComputerBT.begin("Team-11-White-Stripe");
  pinMode(LED, OUTPUT);
}

void loop() {
  // Read it byte-wise....
  if ( ComputerBT.available() ) {
    SensorSerial.write( ComputerBT.read() );
    /* digitalWrite( LED, HIGH );
  } else {
    delay(200);
    digitalWrite( LED, LOW ); */
  }

  if ( SensorSerial.available() ) {
    ComputerBT.write( SensorSerial.read() );
    digitalWrite( LED, HIGH );
  } else {
    delay(200);
    digitalWrite( LED, LOW );
  }
    

}