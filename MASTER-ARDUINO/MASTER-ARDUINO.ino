#define ComputerSerial Serial3  // Change to Serial for computer control; Serial3 for bluetooth control;



/* ====================
   PIN DEFNS
   ==================== */
#define IN_L_1 22
#define IN_L_2 24
#define EN_L 9

#define IN_R_1 50
#define IN_R_2 52
#define EN_R 11

#define LED_R 3
#define LED_G 5
#define LED_B 6

#define FL_TRIG 31
#define FR_TRIG 33
#define R_TRIG 35
#define B_TRIG 37
#define L_TRIG 39
#define G_TRIG 41
#define FL_ECHO A0
#define FR_ECHO A1
#define R_ECHO A2
#define B_ECHO A3
#define L_ECHO A4
#define G_ECHO A5

// According to doc (https://www.arduino.cc/reference/en/language/functions/analog-io/analogwrite/), the ..._SET pins have PWM capability
#define ARM_SET  44
#define GRIP_SET 46


// ULTRAONIC CONFIG....
#define US_DELAY     10
#define TIME_TO_DIST (0.034 * 0.5)

// MOTION CONFIG...
#define SPEED_L 0.905
#define SPEED_R 1.0

#define LIN_SPEED 160
#define LIN_DURATION 600
#define ROT_SPEED 85
#define ROT_DURATION 300

#define DATA_BYTE '~'

// SERIAL CONFIG....
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

// GRIPPER CONFIG...
#define ARM_DOWN    0
#define ARM_UP      255
#define GRIP_OPEN   0
#define GRIP_CLOSED 255



/* ==================
   VARS
   ================== */
// Timestamps to turn off motors...
unsigned long motor_R_start = 0;
unsigned long motor_L_start = 0;

unsigned long motor_R_end = 0;
unsigned long motor_L_end = 0;

unsigned long motor_R_stopped = 0;
unsigned long motor_L_stopped = 0;

unsigned int time[6];
int distance[7];



/* =================
   MISC FUNCTIONS 
   ================= */
int apply_factor(int speed, float factor) {
  return int((float)speed * factor);
}

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
  start_motor_R(1, (long)duration, 1);
  start_motor_L(1, (long)duration, 1);
}

void go_backward(unsigned int duration) {
  start_motor_R(-1, (long)duration, 1);
  start_motor_L(-1, (long)duration, 1);
}

void go_clock(unsigned int duration) {
  start_motor_R(-1, (long)duration, 0);
  start_motor_L(1, (long)duration, 0);
}

void go_cclock(unsigned int duration) {
  start_motor_R(1, (long)duration, 0);
  start_motor_L(-1, (long)duration, 0);
}

void start_motor_R(int direction, long duration, int is_lin) {
  unsigned long now = millis();

  if (direction < 0) {
    digitalWrite(IN_R_1, LOW);
    digitalWrite(IN_R_2, HIGH);
  } else if (direction > 0) {
    digitalWrite(IN_R_1, HIGH);
    digitalWrite(IN_R_2, LOW);
  }

  analogWrite(EN_R, apply_factor(is_lin ? LIN_SPEED : ROT_SPEED, SPEED_R));

  motor_R_end = now + duration;
  motor_R_start = now;
  motor_R_stopped = 0;
}

void start_motor_L(int direction, long duration, int is_lin) {
  unsigned long now = millis();

  if (direction < 0) {
    digitalWrite(IN_L_1, LOW);
    digitalWrite(IN_L_2, HIGH);
  } else if (direction > 0) {
    digitalWrite(IN_L_1, HIGH);
    digitalWrite(IN_L_2, LOW);
  }

  analogWrite(EN_L, apply_factor(is_lin ? LIN_SPEED : ROT_SPEED, SPEED_L));

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
   GRIPPERS 
   ================= */
void set_gripper( int open ) {
  if ( open )
    analogWrite( GRIP_SET, GRIP_OPEN );
  else
    analogWrite( GRIP_SET, GRIP_CLOSED );
}

void set_arm( int up_state ) {
  if ( up_state )
    analogWrite( ARM_SET, ARM_UP );
  else
    analogWrite( ARM_SET, ARM_DOWN);
  if ( up_state ) 
    ComputerSerial.println("Setting arm UP!");
  else
    ComputerSerial.println("Setting arm DOWN!");
}

void gripper_receive_command() {
  char motion = blocking_peek();
    switch ( motion ) {
      case 'U': { /* UP */
        set_arm(1);
        break;
      }

      case 'D' : { /* DOWN */
        set_arm(0);
        break;
      }

      case 'O' : { /* OPEN */
        set_gripper(1);
        break;
      }

      case 'C' : { /*CLOSED */
        set_gripper(0);
        break;
      }

      default : {
        /* Return without ACK */
        return;
      }
    }
    // Remove byte from buffer, send ACK
    motion = ComputerSerial.read();
    ComputerSerial.println(GRIP_ACK);
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
  time[0] = SensorPulseDuration(FL_TRIG, FL_ECHO);
  delay(US_DELAY);
  time[1] = SensorPulseDuration(FR_TRIG, FR_ECHO);
  delay(US_DELAY);
  time[2] = SensorPulseDuration(R_TRIG, R_ECHO);
  delay(US_DELAY);
  time[3] = SensorPulseDuration(B_TRIG, B_ECHO);
  delay(US_DELAY);
  time[4] = SensorPulseDuration(L_TRIG, L_ECHO);
  delay(US_DELAY);
  time[5] = SensorPulseDuration(G_TRIG, G_ECHO);
  delay(US_DELAY);
}

void compute_distances() {
  distance[0] = time[0] * TIME_TO_DIST;
  distance[1] = time[1] * TIME_TO_DIST;
  distance[2] = time[2] * TIME_TO_DIST;
  distance[3] = time[3] * TIME_TO_DIST;
  distance[4] = time[4] * TIME_TO_DIST;
  distance[5] = time[5] * TIME_TO_DIST;
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
  ComputerSerial.print(";5_");
  ComputerSerial.println(distance[5]);
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

      
      case 'G' : { /* GRIPPER */
        gripper_receive_command();
        break;
      }


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
    }
  }
}



/* =================
   SETUP
   ================= */
#define IN_L_1 22
void setup() {
  ComputerSerial.begin(9600);
  Serial.begin(9600);

  pinMode(IN_L_1, OUTPUT);   pinMode(IN_L_2, OUTPUT);   pinMode(EN_L, OUTPUT);
  pinMode(IN_R_1, OUTPUT);   pinMode(IN_R_2, OUTPUT);   pinMode(EN_R, OUTPUT);

  pinMode(LED_R, OUTPUT);    pinMode(LED_G, OUTPUT);    pinMode(LED_B, OUTPUT);

  pinMode(FL_TRIG, OUTPUT);  pinMode(FL_ECHO, INPUT);
  pinMode(FR_TRIG, OUTPUT);  pinMode(FR_ECHO, INPUT);
  pinMode(R_TRIG, OUTPUT);   pinMode(R_ECHO,  INPUT);
  pinMode(B_TRIG, OUTPUT);   pinMode(B_ECHO,  INPUT);
  pinMode(L_TRIG, OUTPUT);   pinMode(L_ECHO,  INPUT);
  pinMode(G_TRIG, OUTPUT);   pinMode(G_ECHO,  INPUT);
  
  pinMode(GRIP_SET, OUTPUT); pinMode(ARM_SET,  OUTPUT);
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