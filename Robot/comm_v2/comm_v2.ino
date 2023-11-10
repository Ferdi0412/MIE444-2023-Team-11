#include "BluetoothSerial.h"

// #define LED 2

BluetoothSerial ComputerBT;

#define RXD2 16
#define TXD2 17

void setup() {
  // put your setup code here, to run once:
  // Serial.begin(9600);
  ComputerBT.begin("Team-11-White-Stripe");
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  // pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if ( ComputerBT.available() ) {
        Serial2.write( ComputerBT.read() );
        // digitalWrite(LED, HIGH);
  }

  
  if ( Serial2.available() ) {
    ComputerBT.write( Serial2.read() );
    // digitalWrite(LED, HIGH);
  }
}
