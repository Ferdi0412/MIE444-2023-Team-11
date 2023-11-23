#include <util/atomic.h>

/* ======= SERIAL SETUP ======= */
#define READ_COUNT(err_code) ((err_code) - 1)
#define READ_RETRIES 2
#define READ_DELAY   2
char identifier = -1;

char write_buffer[1024];

/* ======= MOTOR PINS ========== */
// Motor
#define PPR     420 /* Pulses per revolution */
#define MAX_RPM 100

// PID
#define KP 1
#define KI 10

// Pins
#define ENCA 2
#define ENCB 3
#define PWM 6
#define IN1 5
#define IN2 4

/* ======= MOTOR CONTROL SETUP ========== */
// unsigned long prev_time = 0;
unsigned long prev_pos  = 0;

volatile unsigned long  prev_time;
volatile unsigned long  pos_i   = 0;
// volatile unsigned float speed_i = 0;

unsigned long  target_pos    = 0;
float target_speed = 0;

double         filtered_speed = 0; // Previously v1Filt
float curr_speed = 0;
float prev_speed     = 0;

float err_integral = 0;
int   pwm_out      = 0;
int   direction_input = 0;

/* ======= STARTUP ========== */
void setup() {
  Serial.begin(9600);

  pinMode(ENCA, INPUT); pinMode(ENCB, INPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(PWM, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(ENCA), encoder_increment, RISING);

  // TODO: Remove this...
  // target_pos      = 10000;
  // target_speed    = 100;
  // direction_input = 1;
}

/* ======= MAIN ========== */
void loop() {
  // Handle Serial communication
  receive_cmd();

  // Atomically read pos (prevent issues with interrupts)
  unsigned int pos; ATOMIC_BLOCK(ATOMIC_RESTORESTATE) { pos=pos_i; }

  // If reached target, set target speed to 0
  if ( pos >= target_pos ) { target_speed = 0; }

  // Calculate time since last, and rate of pulses
  unsigned long curr_time = micros();
  float delta_time = ( (float) curr_time - prev_time ) / 1.0e6;

  float delta_pos  = fabs( ( (float) pos - prev_pos ) / delta_time );

  // Translate pulses to rotational speed
  curr_speed = delta_pos / PPR * 60;

  // Low pass filter of some kind
  filtered_speed = (0.854 * filtered_speed) + (0.0728 * curr_speed) + (0.0728 * prev_speed);

  // Store last iteration states
  prev_pos = pos; prev_time = curr_time; prev_speed = curr_speed;

  // Error to adjust
  double err = target_speed - filtered_speed;

  err_integral += (err * KI);

  double new_speed = (KP * err) + (KI * err_integral);

  // Binary speed representation
  int direction = direction_input * (1 ? new_speed >= 0 : -1);

  if ( ( pwm_out = (int) fabs(new_speed) ) > 255 ) { pwm_out = 255; };

  set_motor_state(direction, pwm_out);
}

/* ======= MOTOR FUNCTIONS ========== */
void set_motor_state( int direction, int pwm_duty_cycle ) {
  analogWrite(PWM, pwm_duty_cycle);
  if ( direction > 0 ) {
    // Turn "forwards"
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }
  else if ( direction < 0 ) {
    // Turn "backwards"
    digitalWrite(IN2, LOW);
    digitalWrite(IN1, HIGH);
  }
  else {
    // "STOP"
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
  }
}

/* ======= COMMUNICATION FUNCTIONS ========== */
void assign_position(char* buffer) {
  *((int*) buffer) = prev_pos;
}

void write_position_msg(char target_id) {
  write_buffer[0] = target_id;
  write_buffer[1] = identifier;
  assign_position( &(write_buffer[2]) );
  write_buffer[4] = '\n';
  Serial.write(write_buffer, 5);
}

void receive_cmd(){
  if (Serial.available()){
    char byte_0 = Serial.read();

    switch ( byte_0 ) {
    
      // Movement command
      case 'M': {
        char motor_id; int new_pos; float new_speed;
        if ( read_char(Serial, &motor_id) )
          break;
        if ( read_int(Serial, &new_pos) )
          break;
        if ( read_float(Serial, &new_speed) )
          break;
        // If successfully read all values, respond with position message begginning with 'M'
        write_position_msg('M');
        // If all values successfully read from message, act upon them; ALSO, enforce 60 RPM as max speed
        target_pos   = new_pos; target_speed = (fabs(new_speed) < MAX_RPM) ? fabs(new_speed) : MAX_RPM;
        direction_input = (new_speed >= 0) ? 1 : -1;
        // Reset position tracker
        pos_i = 0;
        // DEBUGGING
        // Serial.println("Valid movement command!"); Serial.print("Travelling at speed "); Serial.print(target_speed); Serial.print("; To pulse "); Serial.println(new_pos);
        // EXIT
        break;
      }

        // Stop command
        case 'S': {
          write_position_msg('S');
          target_pos = 0; target_speed = 0; direction_input = 0;
          set_motor_state(0, 0);
          // Immediately stop motion?
          // digitalWrite(PWM, LOW);
          break;
        }

      case 'P': {
        write_position_msg('P');
        break;
      }
      
      case 'A': {
        write_buffer[0] = 'A';
        write_buffer[1] = identifier;
        write_buffer[2] = (char) ( 0 == target_speed );
        write_buffer[3] = '\n';
        Serial.write(write_buffer, 4);
        break;
      }
      
      case 'X': {
        char new_id;
        if ( read_char(Serial, &new_id) )
          break;
        identifier = new_id;
        break;
      }
      
      default: {
        // If invalid, do nothing
        break;
      }
    }
  }
}


/* ======= INTERRUPT ========== */
void encoder_increment(){
  // Read encoder B when ENCA rises
  int b = digitalRead(ENCB);
  pos_i ++;
}


/* ======= BYTE ENCODING FUNCTIONS ========== */
char read_char(Stream &serialport, char* target) {
  for ( int j = 0; j < READ_RETRIES; j++ ) {
    if ( serialport.available() ) {
      *target = serialport.read();
      return 0;
    }
    #ifdef READ_DELAY
      delay(READ_DELAY);
    #endif
  }
  return -1;
}

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
      #ifdef READ_DELAY
        delay(READ_DELAY);
      #endif
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
      #ifdef READ_DELAY
        delay(READ_DELAY);
      #endif
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