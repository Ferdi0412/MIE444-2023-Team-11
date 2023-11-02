/*Note:

This is intended for use with the ESP32 board. To upload the code, you must press the "Boot" button while uploading...
(On the actual board, the "B" is rubbed off, so it looks like "oot")
Otherwise you will have "uploading error: exit status 2"

Also note that for some reason, compiling and uploading to the ESP32 is MUCH slower than to a regular arduino board.

Tutorial on getting address: https://www.youtube.com/watch?v=fxvoNpiqipQ
Quick tutorial for bluetooth on esp32: https://randomnerdtutorials.com/esp32-bluetooth-classic-arduino-ide/

*/

// MOTION COMMANDS
#define FORWARD    0x01
#define BACKWARD   0x02
#define LEFT       0x03
#define RIGHT      0x04
#define ROT_CLOCK  0x05
#define ROT_CCLOCK 0x06
#define IN_MOV     0x07
#define STOP       0x08
#define PROG       0x09

// SENSOR COMMANDS
#define ALL_SENSORS    0x10
#define GYRO           0x30
#define COMPASS        0x40
#define ALL_ULTRASONIC 0x20

#define ULTRASONIC_1   0x21
#define ULTRASONIC_2   0x22
#define ULTRASONIC_3   0x23
#define ULTRASONIC_4   0x24
#define ULTRASONIC_5   0x25
#define ULTRASONIC_6   0x26

/*=========================================== 
  ================= IMPORTS =================
  =========================================== */
#include "BluetoothSerial.h"
#include "esp_bt_device.h"



/*========================================================= 
  ================= FUNCTION DECLARATIONS =================
  ========================================================= */
int get_mac_addr(char *string, int string_len);

void read_serial();



/*============================================= 
  ================= variables =================
  ============================================= */
BluetoothSerial SerialBT;



/*========================================= 
  ================= SETUP =================
  ========================================= */
void setup() {
  Serial.begin(9600); // For monitor in Arduino IDE

  if ( !SerialBT.begin("MIE444-Group-11") )
    Serial.println("Could not setup bluetooth!");

  char str[17];
  if ( get_mac_addr(str, 17) )
    Serial.println("Error fetching MAC address!");
  
  else {
    Serial.print("MAC address: ");
    Serial.println(str);
  }

  Serial.println("Now pairable...");
}

/*======================================== 
  ================= MAIN =================
  ======================================== */
void loop() {
  char str[25];

  read_serial();

  // if ( Serial.available() ) {
  //   int val = Serial.read();
  //   // sprintf(str, "%str", val);
  //   Serial.println(val);
  //   // Serial.println(str);
  // }
  
  // If SerialBT.available() -> Message received
  if ( SerialBT.available() ) {
    // Send to Arduino monitor...
    Serial.write(SerialBT.read());
  }
}



/*============================================= 
  ================= FUNCTIONS =================
  ============================================= */
int get_mac_addr(char *string, int string_len) {
  /* Function that assigns string the mac address of this board. */
  if ( string_len < 17 )
    return 1;
  const uint8_t* address = esp_bt_dev_get_address();
  for ( int i = 0; i < 6; i++ ) {
    int idx = 3 * i;
    sprintf( &(string[idx]), "%02X:", (int) address[i] );
  }
  return 0;
}


void read_serial() {
  char buffer[24];

  float dist;

  int bytes_available = Serial.available();
  char byte_one;
  
  if ( bytes_available > 0 )
    byte_one = Serial.read();
  else
    return;

  switch (byte_one) {
    case FORWARD:
      dist = get_value_from_serial();
      sprintf(buffer, "%f", dist);
      Serial.println(buffer);
      break;

    case BACKWARD:
      dist = get_value_from_serial();
      sprintf(buffer, "%f", dist);
      Serial.println(buffer);
      break;

    default:
      sprintf(buffer, "%f", 0);
      Serial.println(buffer);
      break;
  }
}


float get_value_from_serial() {
  float *val;
  for ( int i = 0; i < 4; i++ ) {
    ((char *) val)[i] = Serial.read();
  }
  return *val;
}



int is_motor_cmd(char byte_one) {
  if ( byte_one << 4 )
    return 1;
  else
    return 0;
}