#include "BluetoothSerial.h"

#define LED 2

BluetoothSerial ComputerBT;

#define RXD2 16
#define TXD2 17

void setup() {
  // put your setup code here, to run once:
  // Serial.begin(9600);
  // ComputerBT.begin("Team-11-Stripeless");
  ComputerBT.begin("Team-11-White-Stripe");
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  pinMode(LED, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  // Purely for displaying stuff... Remove later
  delay(200);
  digitalWrite(LED, LOW);

  while ( ComputerBT.available() ) {
    digitalWrite(LED, HIGH);
    Serial2.write( ComputerBT.read() );
  }

  while ( Serial2.available() ) {
    digitalWrite(LED, HIGH);
    ComputerBT.write( Serial2.read() );
  }
}
