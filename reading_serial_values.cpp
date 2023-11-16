char read_char(Stream &serialport, char* target) {
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
  if ( serialport.available() )
    *target = serialport.read();
  else
    return -1;
  return 0;
}

char read_short(Stream &serialport, short* target) {
  /*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  short val;
  if ( read_short(Serial, & val ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Short! -> ");
    Serial.println(val);
  }
  */
  short val;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(short); i++ ) {
    if ( serialport.available() )
      ((char *) &val)[i] = serialport.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

char read_int(Stream &serialport, int* target) {
  /*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  int val;
  if ( read_int(Serial, & val ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Integer! -> ");
    Serial.println(val);
  }
  */
  int val;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(int); i++ ) {
    if ( serialport.available() )
      ((char *) &val)[i] = serialport.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

char read_long(Stream &serialport, long* target) {
  /*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  long val;
  if ( read_long(Serial, & val ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Long! -> ");
    Serial.println(val);
  }
  */
  long val;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(long); i++ ) {
    if ( serialport.available() )
      ((char *) &val)[i] = serialport.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

char read_float(Stream serialport, float* target) {
  /*Assigns value read from some serial connection to target. Returns 0 if successful.

  To get value, do the following:
  // == CODE EXAMPLE ==
  float val;
  if ( read_float(Serial, & val ) {
    // Invalid input from Serial...
  }
  else {
    // You have an actual, valid value!
    Serial.print("Received a correctly encoded Float! -> ");
    Serial.println(val);
  }
  */
  float val;
  // Read required number of bytes...
  for ( int i = 0; i < sizeof(float); i++ ) {
    if ( serialport.available() )
      ((char *) &val)[i] = serialport.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}
