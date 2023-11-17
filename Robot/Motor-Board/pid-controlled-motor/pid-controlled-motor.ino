#include <util/atomic.h>


/* ======= SERIAL READING ======= */
#define READ_COUNT(err_code) ((err_code) - 1)
#define READ_RETRIES 2
char identifier = -1;

char write_buffer[1024];

char read_char(Stream &serialport, char* target) {
  for ( int j = 0; j < READ_RETRIES; j++ ) {
    if ( serialport.available() ) {
      *target = serialport.read();
      return 0;
    }
  }
  return -1;
}

void write_position_msg(char target_id) {
  write_buffer[0] = target_id;
  write_buffer[1] = identifier;
  assign_position( &(write_buffer[2]) );
  write_buffer[4] = '\n';
  Serial.write(write_buffer, 5);
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




/* ======= MOTOR CONTROL SETUP ========== */
// Pins
#define ENCA 2
#define ENCB 3
#define PWM 9
#define IN1 8
#define IN2 7

// globals
int target_pos = 0;
long prevT = 0;
int posPrev = 0;
// Use the "volatile" directive for variables
// used in an interrupt
volatile int pos_i = 0;
volatile long prevT_i = 0;

float v1Filt = 0;
float v1Prev = 0;
float vt = 0;
int dir = -1;

float eintegral = 0;



/* ===== SETUP ===== */
void setup() {
  Serial.begin(9600);

  pinMode(ENCA,INPUT);
  pinMode(ENCB,INPUT);
  pinMode(PWM,OUTPUT);
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);

  attachInterrupt(digitalPinToInterrupt(ENCA),readEncoder,RISING);
}

/* ====== MAIN ===== */
void loop() {
  // Read and respond to serial coms.
  recieve_cmd();

  // Stop if past target...
  if ( posPrev > target_pos ) {
    vt = 0;
    setMotor(1, PWM, 0, IN1, IN2);
  }


  // read the position in an atomic block
  // to avoid potential misreads
  int pos = 0;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE){
    pos = pos_i;
  }

  // Compute velocity with method 1
  long currT = micros();
  float deltaT = ((float) (currT-prevT))/1.0e6;
  float velocity1 = (pos - posPrev)/deltaT;
  posPrev = pos;
  prevT = currT;

  // Convert count/s to RPM
  float v1 = velocity1/420*60.0;

  // Low-pass filter (25 Hz cutoff)
  v1Filt = 0.854*v1Filt + 0.0728*v1 + 0.0728*v1Prev;
  v1Prev = v1;

  // Compute the control signal u
  float kp = 2;
  float ki = 10;
  float e = vt-v1Filt;
  eintegral = eintegral + e*deltaT;
  
  float u = kp*e + ki*eintegral;

  // Set the motor speed and direction
  //receieve input speed (target speed) and distance (speed * time), move to that, ideally receive progress (how far are you from reaching the target distance), accept a stop command 

  int pwr = (int) fabs(u);
  if(pwr > 255){
    pwr = 255;
  }

  setMotor(dir,pwr,PWM,IN1,IN2);
    delay(1);

  delay(1);
}

/* ======== FUNCTIONS ======= */
void setMotor(int dir, int pwmVal, int pwm, int in1, int in2){
  analogWrite(pwm,pwmVal); // Motor speed
  if(dir == 1){ 
    // Turn one way
    digitalWrite(in1,HIGH);
    digitalWrite(in2,LOW);
  }
  else if(dir == -1){
    // Turn the other way
    digitalWrite(in1,LOW);
    digitalWrite(in2,HIGH);
  }
  else{
    // Or dont turn
    digitalWrite(in1,LOW);
    digitalWrite(in2,LOW);    
  }
}

void readEncoder(){
  // Read encoder B when ENCA rises
  int b = digitalRead(ENCB);
  int increment = 0;
  if(b>0){
    // If B is high, increment forward
    increment = 1;
  }
  else{
    // Otherwise, increment backward
    increment = 1; // -1
  }
  pos_i = pos_i + increment;
}

void recieve_cmd(){
  if (Serial.available()){
    char byte_0 = Serial.read();
    // Serial.print("Responding to ");
    // Serial.println(byte_0);

    switch ( byte_0 ) {
    
      // Movement command
      case 'M': {
        Serial.println("Valid move!");
        char motor_id; int new_pos; float new_speed;
        if ( read_char(Serial, &motor_id) )
          break;
        Serial.println("Nice ID");
        if ( read_int(Serial, &new_pos) )
          break;
        Serial.println("Now for the SPEED!!!");
        if ( read_float(Serial, &new_speed) )
          break;
        write_position_msg('M');
        Serial.println("Valid movement command!");
        Serial.print("Travelling at speed ");
        Serial.print(new_speed);
        Serial.print("; To pulse ");
        Serial.println(new_pos);
        int old_pos = target_pos;
        target_pos = new_pos;
        // Reset position...
        posPrev = 0;
        vt = fabs(new_speed);
        setMotor(1, 100, PWM, IN1, IN2);
        break;
      }

        // Stop command
        case 'S': {
          write_position_msg('S');
          target_pos = 0;
          vt = 0;
          setMotor(1, 0, PWM, IN1, IN2);
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
        write_buffer[2] = (char) (target_pos > posPrev);
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
        // Serial.println("Unrecognizable command!");
        break;
      }
    }
  }
  delay(100);
}

void assign_position(char* buffer) {
  *((int*) buffer) = posPrev;
}