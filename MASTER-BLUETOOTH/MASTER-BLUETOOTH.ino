#include "BluetoothSerial.h"

// LED to blink to indicate communication
#define LED_ON_MSG
#define LED 2
#define LED_MS_ON 200
unsigned long time_off = 0;

// Pins to communicate with Robot through
#define RXD2 16
#define TXD2 17
#define RobotSerial Serial2

// Buffer coms, to try speed it up
#define BUFFER_LEN 128
char buffer[BUFFER_LEN];

// Bluetooth Serial
BluetoothSerial ComputerBT;

// Buffer then send function
void buffered_send(Stream &stream_in, Stream &stream_out) {
  unsigned int bytes_to_send;
  
  bytes_to_send = stream_in.available();
  if ( bytes_to_send > BUFFER_LEN )
    bytes_to_send = BUFFER_LEN;
  
  if ( bytes_to_send > 0 ) {
    #ifdef LED_ON_MSG
      time_off = millis() + LED_MS_ON;
      digitalWrite(LED, HIGH);
    #endif

    stream_in.readBytes(buffer, bytes_to_send);

    stream_out.write(buffer, bytes_to_send);
  }
}

// SETUP
void setup() {
  ComputerBT.begin("Team-11-Robot");
  RobotSerial.begin(9600);
  #ifdef LED_ON_MSG
    pinMode(LED, OUTPUT);
  #endif
}

// MAIN
void loop() {
  #ifdef LED_ON_MSG
    if ( millis() > time_off ) {
      digitalWrite(LED, LOW);
    }
  #endif

  buffered_send(ComputerBT, RobotSerial);
  buffered_send(RobotSerial, ComputerBT);
}