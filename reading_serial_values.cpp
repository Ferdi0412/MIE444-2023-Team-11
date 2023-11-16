// ===== INCLUDE THE FOLLOWING #define LINES =====
#define READ_COUNT(err_code) ((err_code) - 1)
#define READ_RETRIES 2

/* CONVOLUDED, use only if confident in C.

// == CODE EXAMPLE ==
int *val;
int err_code;
if ( err_code = read_bytes(SerialInput, (char*) val, sizeof(int)) ) {
  // Printing number of bytes read...
  SerialOutput.print("Failed to read <INT>! ");
  SerialOutput.print(READ_COUNT(err_code));
  SerialOutput.print(" of ");
  SerialOutput.print(sizeof(int));
  SerialOutput.print(" bytes read!");

  // Printing characters read
  for ( int i = 0; i < READ_COUNT(err_code); i++ ) {
    SerialOutput.print("Byte [");
    SerialOutput.print(i);
    SerialOutput.print("] := ");
    SerialOutput.println(val[i]);
  }
  else {
    SerialOutput.print("Read value: ");
    SerialOutput.println(*val);
  }
}

*/
int read_bytes(Stream &serialport, char* target, int bytes_to_read) {
  for ( int i = 0; i < bytes_to_read; i++ ) {
    for ( int j = 0; j < READ_RETRIES; j++ ) {
      if ( serialport.available() ) {
        target[i] = serialport.read();
        break;
      }
      else if ( j = READ_RETRIES - 1)
        return i + 1;
    }
  }
  return 0;
}

/*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  char val;
  if ( read_char(Serial, & val ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Char! -> ");
    Serial.println(val);
  }
  */
char read_char(Stream &serialport, char* target) {
  for ( int j = 0; j < READ_RETRIES; j++ ) {
    if ( serialport.available() ) {
      *target = serialport.read();
      return 0;
    }
  }
  return -1;
}

/*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  short val;
  if ( read_short(Serial, & val, NULL ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Short! -> ");
    Serial.println(val);
  }
  */
int read_short(Stream &serialport, short* target) {
  short val = 0;
  char  readable_flag;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(short); i++ ) {
    readable_flag = 0;
    // Allow retries, incase bytes aren't immediately available
    for ( int j = 0; j < READ_RETRIES; j++ ) {
      if ( serialport.available() ) {
        readable_flag = 1;
        break;
      }
    }
    if ( readable_flag )
      ((char *) &val)[i] = serialport.read();
    // Allow failed to read bytes to be returned
    else
      return i + 1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

/*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  int val;
  if ( read_int(Serial, & val, NULL ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Integer! -> ");
    Serial.println(val);
  }
  */
int read_int(Stream &serialport, int* target) {
  int  val;
  char readable_flag = 0;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(int); i++ ) {
    // Indicate that no byte readable yet...
    readable_flag = 0;
    for ( int j = 0; j < READ_RETRIES; j++ ) {
      // If value could be read,
      if ( serialport.available() ) {
        readable_flag = 1;
        break;
      }
    }
    if ( readable_flag )
      ((char *) &val)[i] = serialport.read();
    // If too few bytes in serial, return -1
    else
      return i+1; // Return natural number (ie. index + i) of character that failed to read...
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

/*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  long val;
  if ( read_long(Serial, & val, NULL ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Long! -> ");
    Serial.println(val);
  }
  */
char read_long(Stream &serialport, long* target) {
  long val = 0;
  char readable_flag;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(long); i++ ) {
    readable_flag = 0;
    // Allow retries, incase bytes aren't immediately available
    for ( int j = 0; j < READ_RETRIES; j++ ) {
      if ( serialport.available() ) {
        readable_flag = 1;
        break;
      }
    }
    if ( readable_flag )
      ((char *) &val)[i] = serialport.read();
    // Allow failed to read bytes to be returned
    else
      return i + 1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

/*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  float val;
  if ( read_float(Serial, & val, NULL ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Float! -> ");
    Serial.println(val);
  }
  */
char read_float(Stream &serialport, float* target) {
  float val = 0;
  char  readable_flag;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(float); i++ ) {
    readable_flag = 0;
    // Allow retries, incase bytes aren't immediately available
    for ( int j = 0; j < READ_RETRIES; j++ ) {
      if ( serialport.available() ) {
        readable_flag = 1;
        break;
      }
    }
    if ( readable_flag )
      ((char *) &val)[i] = serialport.read();
    // Allow failed to read bytes to be returned
    else
      return i + 1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}
