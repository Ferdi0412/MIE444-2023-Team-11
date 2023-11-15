char read_char(HardwareSerial Com, char* target) {
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
  if ( Com.available() )
    *target = Com.read();
  else
    return -1;
  return 0;
}

char read_int(HardwareSerial Com, int* target) {
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
    if ( Com.available() )
      ((char *) &val)[i] = Com.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

char read_long(HardwareSerial Com, long* target) {
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
    if ( Com.available() )
      ((char *) &val)[i] = Com.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

char read_float(HardwareSerial Com, float* target) {
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
    if ( Com.available() )
      ((char *) &val)[i] = Com.read();
    // If too few bytes in serial, return -1
    else
      return -1;
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}
