#include <Wire.h>
#include <VL53L0X.h>


#define ComputerSerial Serial3  // Change to Serial for computer control; Serial3 for bluetooth control;



/* ====================
   PIN DEFNS
   ==================== */
#define IN_L_1 22
#define IN_L_2 24
#define EN_L   9

#define IN_R_1 23
#define IN_R_2 25
#define EN_R   10

// LEDs need PWM
#define LED_R 3
#define LED_G 5
#define LED_B 6

#define F_TRIG 31
#define F_ECHO A8
#define R_TRIG 39
#define R_ECHO A12
#define B_TRIG 37
#define B_ECHO A11
#define LB_TRIG 35
#define LB_ECHO A10
#define LF_TRIG 33
#define LF_ECHO A9

// According to doc (https://www.arduino.cc/reference/en/language/functions/analog-io/analogwrite/), the ..._SET pins have PWM capability
// #define ARM_SET  44
// #define GRIP_SET 46


#define TOF_FL 0x40
#define TOF_FL_X 51
#define TOF_BL 0x41
#define TOF_BL_X 50
#define TOF_R  0x42
#define TOF_R_X  48

#define TOF_TIMEOUT 500
#define TOF_CONTINUOUS

// === ULTRAONIC CONFIG.... ===
#define US_DELAY     10
#define TIME_TO_DIST (0.034 * 0.5)

// === MOTION CONFIG... ===
#define RAMP_STEPS 3
#define RAMP_DELAY 50

#define SPEED_L 0.905
#define SPEED_R 1.0

#define LIN_SPEED 140
#define LIN_DURATION 600
#define ROT_SPEED 110
#define ROT_DURATION 300

#define DATA_BYTE '~'

// === SERIAL CONFIG.... ===
#define W_ACK    "W-ACK"
#define S_ACK    "S-ACK"
#define Q_ACK    "Q-ACK"
#define E_ACK    "E-ACK"
#define LED_ACK  "LED-ACK"
#define STOP_ACK "STOP-ACK"
#define GRIP_ACK "GRIPPER-ACK"

#define ACTIVE "ACTIVE"
#define NACTIVE "NOT-ACTIVE"

#define READ_RETRIES 2
#define READ_DELAY 2

// === GRIPPER CONFIG... ===
// #define ARM_DOWN    0
// #define ARM_UP      255
// #define GRIP_OPEN   0
// #define GRIP_CLOSED 255



/* ==================
   VARS
   ================== */
VL53L0X sensor_R;
VL53L0X sensor_FL;
VL53L0X sensor_BL;

// Timestamps to turn off motors...
unsigned long motor_R_start = 0;
unsigned long motor_L_start = 0;

unsigned long motor_R_end = 0;
unsigned long motor_L_end = 0;

unsigned long motor_R_stopped = 0;
unsigned long motor_L_stopped = 0;

unsigned int time[5];
int distance[5];



/* =================
   MISC FUNCTIONS 
   ================= */
int apply_factor(int speed, float factor) {
  return int((float)speed * factor);
}

/* =================
   SERIAL FUNCTIONS 
   ================= */
int read_int(int* target) {
  int val;
  char readable_flag = 0;
  // Read required number of bytes...
  for (int i = 0; i < sizeof(int); i++) {
    // Indicate that no byte readable yet...
    readable_flag = 0;
    for (int j = 0; j < READ_RETRIES; j++) {
      // If value could be read,
      if (ComputerSerial.available()) {
        readable_flag = 1;
        break;
      }
#ifdef READ_DELAY
      delay(READ_DELAY);
#endif
    }
    if (readable_flag)
      ((char*)&val)[i] = ComputerSerial.read();
    // If too few bytes in serial, return -1
    else
      return i + 1;  // Return natural number (ie. index + i) of character that failed to read...
  }
  // Assign value to target pointer
  *target = val;
  // Return 0
  return 0;
}

char read_uchar(unsigned char* target) {
  for (int j = 0; j < READ_RETRIES; j++) {
    if (ComputerSerial.available()) {
      *target = ComputerSerial.read();
      return 0;
    }
#ifdef READ_DELAY
    delay(READ_DELAY);
#endif
  }
  return -1;
}


char blocking_peek() {
  for (int j = 0; j < READ_RETRIES; j++) {
    if (ComputerSerial.available())
      return ComputerSerial.peek();
#ifdef READ_DELAY
    else
      delay(READ_DELAY);
#endif
  }
  return -1;
}



void scan_i2c_devices() {
  ComputerSerial.print("D");
  for ( byte i = 8; i < 127; i++ ) {
    Wire.beginTransmission(i);
    byte error = Wire.endTransmission();

    if ( error == 0 ) {
      ComputerSerial.print("_");
      ComputerSerial.print("0x");
      if ( i < 16 ) {
        ComputerSerial.print("0");
      }
      ComputerSerial.print(i, HEX);
    }
  }
  ComputerSerial.println("");
}



char set_i2c_addr( int old_addr, int new_addr, int xshut_pin ) {
  pinMode(xshut_pin, OUTPUT);

  digitalWrite( xshut_pin, LOW );
  delay(20);
  digitalWrite( xshut_pin, HIGH);
  delay(10);
  Wire.beginTransmission( old_addr );
  Wire.write( 0x8A );
  Wire.write( new_addr );
  Wire.endTransmission();

  delay(10);

  // digitalWrite( xshut_pin, HIGH );

  pinMode(xshut_pin, INPUT);
}



/* =================
   LED FUNCTIONS 
   ================= */
int analog_limit(int val) {
  if (val < 0)
    return 0;
  else if (val > 255)
    return 255;
  else
    return val;
}

void set_led(int r, int g, int b) {
  analogWrite(LED_R, analog_limit(r));
  analogWrite(LED_G, analog_limit(g));
  analogWrite(LED_B, analog_limit(b));
}



/* =================
   MOTOR FUNCTIONS 
   ================= */
void go_forward(unsigned int duration) {
  // Start both motors...
  start_motor_R( 1, (long) duration, 0); start_motor_L( 1, (long) duration, 0);

  // Ramp up the speeds...
  ramp_speeds(LIN_SPEED);
}

void go_backward(unsigned int duration) {
  // Start both motors...
  start_motor_R(-1, (long)duration, 0); start_motor_L(-1, (long)duration, 0);

  // Ramp up the speeds...
  ramp_speeds(LIN_SPEED);
}

void go_clock(unsigned int duration) {
  // Start both motors...
  start_motor_R(-1, (long)duration, 0); start_motor_L(1, (long)duration, 0);

  // Ramp up the speeds...
  ramp_speeds(ROT_SPEED);
}

void go_cclock(unsigned int duration) {
  // Start both motors...
  start_motor_R(1, (long)duration, 0); start_motor_L(-1, (long)duration, 0);

  // Ramp up the speeds...
  ramp_speeds(ROT_SPEED);
}

void ramp_speeds( int final_speed ) {
  for ( int i = 1; i < RAMP_STEPS+1; i++ ) {
    int speed = (int) (((float) final_speed) * (((float) i) / RAMP_STEPS));
    set_motor_R_speed(speed);
    set_motor_L_speed(speed);
    delay(RAMP_DELAY);
  }
}

void set_motor_R_speed( int speed ) {
  analogWrite(EN_R, apply_factor(speed, SPEED_R));
}

void set_motor_L_speed( int speed ) {
  analogWrite(EN_L, apply_factor(speed, SPEED_L));
} 

void start_motor_R(int direction, long duration, int speed) {
  unsigned long now = millis();

  if (direction < 0) {
    digitalWrite(IN_R_1, LOW);
    digitalWrite(IN_R_2, HIGH);
  } else if (direction > 0) {
    digitalWrite(IN_R_1, HIGH);
    digitalWrite(IN_R_2, LOW);
  }

  analogWrite(EN_R, apply_factor(speed, SPEED_R));

  motor_R_end = now + duration;
  motor_R_start = now;
  motor_R_stopped = 0;
  
}

void start_motor_L(int direction, long duration, int speed) {
  unsigned long now = millis();

  if (direction < 0) {
    digitalWrite(IN_L_1, LOW);
    digitalWrite(IN_L_2, HIGH);
  } else if (direction > 0) {
    digitalWrite(IN_L_1, HIGH);
    digitalWrite(IN_L_2, LOW);
  }

  analogWrite(EN_L, apply_factor(speed, SPEED_L));

  motor_L_end = now + duration;
  motor_L_start = now;
  motor_L_stopped = 0; 
}

void stop_motor_R() {
  unsigned long now = millis();

  digitalWrite(IN_R_1, LOW);
  digitalWrite(IN_R_2, LOW);
  digitalWrite(EN_R, LOW);

  motor_R_stopped = now;
}

void stop_motor_L() {
  unsigned long now = millis();

  digitalWrite(IN_L_1, LOW);
  digitalWrite(IN_L_2, LOW);
  digitalWrite(EN_L, LOW);

  motor_L_stopped = now;
}

int is_active() {
  return (0 == motor_L_stopped) && (0 == motor_R_stopped);
}

int is_completed() {
  // If still active, motion NOT completed
  if (is_active()) {
    return 0;
    // unsigned long now = millis();
    // return !( now >= motor_R_end ) && ( now >= motor_L_end );
  } else
    return (motor_R_stopped >= motor_R_end) && (motor_L_stopped >= motor_L_end);
}



/* =================
   ULTRASONICS 
   ================= */
unsigned int SensorPulseDuration(int trigPin, int echoPin) {
  unsigned int duration = 0;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH, 30000);
  return duration;
}

void sense() {
  time[0] = SensorPulseDuration(F_TRIG, F_ECHO);
  delay(US_DELAY);
  time[3] = SensorPulseDuration(LB_TRIG, LB_ECHO);
  delay(US_DELAY);
  time[1] = SensorPulseDuration(R_TRIG,  R_ECHO);
  time[4] = SensorPulseDuration(LF_TRIG, LF_ECHO);
  delay(US_DELAY);
  time[2] = SensorPulseDuration(B_TRIG, B_ECHO);
  delay(US_DELAY);
}

void compute_distances() {
  distance[0] = time[0] * TIME_TO_DIST;
  distance[1] = time[1] * TIME_TO_DIST;
  distance[2] = time[2] * TIME_TO_DIST;
  distance[3] = time[3] * TIME_TO_DIST;
  distance[4] = time[4] * TIME_TO_DIST;
}

void send_ultrasonics() {
  sense();

  compute_distances();

  ComputerSerial.print("U_");
  ComputerSerial.print("0_");
  ComputerSerial.print(distance[0]);
  ComputerSerial.print(";1_");
  ComputerSerial.print(distance[1]);
  ComputerSerial.print(";2_");
  ComputerSerial.print(distance[2]);
  ComputerSerial.print(";3_");
  ComputerSerial.print(distance[3]);
  ComputerSerial.print(";4_");
  ComputerSerial.print(distance[4]);
  ComputerSerial.println();
}



/* =================
   TIME OF FLIGHT 
   ================= */
void setup_time_of_flight( VL53L0X sensor, int x_shut_pin, int addr ) {
  digitalWrite(x_shut_pin, HIGH);
  delay(10);
  if ( !sensor.init() ) {
    set_led( 255, 0, 0 );
  }

  sensor.setAddress(addr);
  delay(10);
  pinMode(x_shut_pin, INPUT);
  delay(10);
  #ifdef TOF_CONTINUOUS
    sensor.startContinuous();
  #else
    sensor.setTimeout(TOF_TIMEOUT);
  #endif
}



uint16_t get_time_of_flight( VL53L0X sensor ) {
  #ifdef TOF_CONTINUOUS
    return sensor.readRangeContinuousMillimeters();
  #else
    return sensor.readRangeSingleMillimeters();
  #endif
}



void print_time_of_flight( uint16_t reading ) {
  if ( reading == 65535 )
    ComputerSerial.print("TIMEOUT");
  else
    ComputerSerial.print(reading);
}



void print_time_of_flight() {
  ComputerSerial.print("T_R_");
  print_time_of_flight(get_time_of_flight(sensor_R));
  ComputerSerial.print(";BL_");
  print_time_of_flight(get_time_of_flight(sensor_BL));
  ComputerSerial.print(";FL_");
  print_time_of_flight(get_time_of_flight(sensor_FL));
  ComputerSerial.println();
}



/* =================
   SERIAL
   ================= */
void receive_send() {
  while (ComputerSerial.available()) {
    unsigned int duration;
    char cmd = ComputerSerial.read();

    switch (cmd) {
      case 'U':
        { /* U-FETCH-ULTRASONICS */
          send_ultrasonics();
          break;
        }

      case 'W':
        { /* W-GO-FORWARDS */
          duration = LIN_DURATION;
          if ((blocking_peek() == DATA_BYTE) && (ComputerSerial.read() == DATA_BYTE) && read_int(&duration)) { /*duration is now updated...*/ }
          go_forward(duration);
          ComputerSerial.println(W_ACK);
          break;
        }

      case 'S':
        { /* S-GO-BACKWARDS */
          duration = LIN_DURATION;
          if ((blocking_peek() == DATA_BYTE) && (ComputerSerial.read() == DATA_BYTE) && read_int(&duration)) { /*duration is now updated...*/ }
          go_backward(duration);
          ComputerSerial.println(S_ACK);
          break;
        }

      case 'Q':
        { /* Q-GO-COUNTER-CLOCKWISE */
          duration = ROT_DURATION;
          if ((blocking_peek() == DATA_BYTE) && (ComputerSerial.read() == DATA_BYTE) && read_int(&duration)) { /*duration is now updated...*/ }
          go_cclock(duration);
          ComputerSerial.println(Q_ACK);
          break;
        }


      case 'E':
        { /* E-GO-CLOCKWISE */
          duration = ROT_DURATION;
          if ((blocking_peek() == DATA_BYTE) && (ComputerSerial.read() == DATA_BYTE) && read_int(&duration)) { /*duration is now updated...*/ }
          go_clock(duration);
          ComputerSerial.println(E_ACK);
          break;
        }


      case 'X':
        { /* X-FORCE-STOP */
          stop_motor_R();
          stop_motor_L();
          ComputerSerial.println(STOP_ACK);
          break;
        }


      case 'A':
        { /* IS-ACTIVE */
          if (is_active())
            ComputerSerial.println(ACTIVE);
          else
            ComputerSerial.println(NACTIVE);
          break;
        }


      case 'L':
        { /* LED */
          // Try to read r, g, b from message
          unsigned char r, g, b;
          if ((!read_uchar(&r)) && (!read_uchar(&g)) && (!read_uchar(&b))) {  // Add block_until_char_avail_count(...)???
            set_led((int)r, (int)g, (int)b);
            ComputerSerial.println(LED_ACK);
          } else { /* Otherwise, assume values are 0 */
            set_led(0, 0, 0);
            ComputerSerial.println(LED_ACK);
          }
          break;
        }

      
      // case 'G' : { /* GRIPPER */
      //   gripper_receive_command();
      //   break;
      // }


      case 'P':
        { /* PROGRESS */
          if (is_completed()) {
            // Check how long before it stopped compared to how long it should have run. Necessary in case it was stopped by 'X'.
            float prog_R = ((double)motor_R_stopped - motor_R_start) / ((double)motor_R_end - motor_R_start);
            float prog_L = ((double)motor_L_stopped - motor_L_start) / ((double)motor_L_end - motor_L_start);
            // Ser 1.0 as max for both
            prog_R = prog_R > 1 ? 1.0 : prog_R;
            prog_L = prog_L > 1 ? 1.0 : prog_L;
            // Print f"P_{progress as percentage}"
            ComputerSerial.print("P_");
            ComputerSerial.println(100 * (prog_R + prog_L) / 2);
          } else {
            // Check how long it has run compared to how long it should run for.
            unsigned long now = millis();
            double prog_R = ((double)now - motor_R_start) / ((double)motor_R_end - motor_R_start);
            double prog_L = ((double)now - motor_L_start) / ((double)motor_L_end - motor_L_start);
            // Print f"P_{progress as percentage}"
            ComputerSerial.print("P_");
            ComputerSerial.println(100 * (prog_R + prog_L) / 2);
          }
          break;
        }
      
      case 'I' : {
        scan_i2c_devices();
        break;
      }

      case 'T': {
        print_time_of_flight();
        break;
      }
    }
  }
}



/* =================
   SETUP
   ================= */
#define IN_L_1 22
void setup() {
  Wire.begin();

  ComputerSerial.begin(9600);
  delay(100);
  Serial.begin(9600);

  pinMode(LED_R, OUTPUT);    pinMode(LED_G, OUTPUT);    pinMode(LED_B, OUTPUT);

  // LED to indicate SETUP started...
  set_led(120, 180, 20);

  // sensor_right.init();
  // sensor_right.setAddress(0x29);

  pinMode(IN_L_1, OUTPUT);   pinMode(IN_L_2, OUTPUT);   pinMode(EN_L, OUTPUT);
  pinMode(IN_R_1, OUTPUT);   pinMode(IN_R_2, OUTPUT);   pinMode(EN_R, OUTPUT);

  pinMode(F_TRIG,  OUTPUT);  pinMode(F_ECHO,  INPUT);
  pinMode(R_TRIG,  OUTPUT);  pinMode(R_ECHO,  INPUT);
  pinMode(B_TRIG,  OUTPUT);  pinMode(B_ECHO,  INPUT);
  pinMode(LF_TRIG, OUTPUT);  pinMode(LF_ECHO, INPUT);
  pinMode(LB_TRIG, OUTPUT);  pinMode(LB_ECHO, INPUT);
  // pinMode(GRIP_SET, OUTPUT); pinMode(ARM_SET,  OUTPUT);
  
  Serial.println("SETUP...");

  delay(100);


  #ifdef TOF_CONTINUOUS
    pinMode(TOF_R_X, OUTPUT);  digitalWrite(TOF_R_X, LOW);
    pinMode(TOF_BL_X, OUTPUT); digitalWrite(TOF_BL_X, LOW);
    pinMode(TOF_FL_X, OUTPUT); digitalWrite(TOF_FL_X, LOW);
    setup_time_of_flight( sensor_R, TOF_R_X, TOF_R );
    setup_time_of_flight( sensor_BL, TOF_BL_X, TOF_BL );
    setup_time_of_flight( sensor_FL, TOF_FL_X, TOF_FL );
  #else
    set_i2c_addr( 0x29, TOF_R,  TOF_R_X  );
    set_i2c_addr( 0x29, TOF_BL, TOF_BL_X );
    set_i2c_addr( 0x29, TOF_FL, TOF_FL_X );

    sensor_R.init();  sensor_R.setAddress(TOF_R);   sensor_R.setTimeout(TOF_TIMEOUT);
    sensor_BL.init(); sensor_BL.setAddress(TOF_BL); sensor_BL.setTimeout(TOF_TIMEOUT);
    sensor_FL.init(); sensor_FL.setAddress(TOF_FL); sensor_FL.setTimeout(TOF_TIMEOUT);
  #endif

  Serial.println("SETUP END...");

  // LED to indicate SETUP ended...
  set_led(0, 120, 120);
}



/* =================
   MAIN
   ================= */
void loop() {
  receive_send();

  unsigned long now = millis();

  if (now > motor_R_end)
    stop_motor_R();

  if (now > motor_L_end)
    stop_motor_L();
}