#include <util/atomic.h>

// Pins
#define ENCA 2
#define ENCB 3
#define PWM 9
#define IN1 8
#define IN2 7

// globals
long prevT = 0;
int posPrev = 0;
// Use the "volatile" directive for variables
// used in an interrupt
volatile int pos_i = 0;
volatile float velocity_i = 0;
volatile long prevT_i = 0;
int setpos = 3000;

float v1Filt = 0;
float v1Prev = 0;
int target_speed = 0;
int direction_input = -1;

float eintegral = 0;

void setup() {
  Serial.begin(9600);

  pinMode(ENCA,INPUT);
  pinMode(ENCB,INPUT);
  pinMode(PWM,OUTPUT);
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);

  attachInterrupt(digitalPinToInterrupt(ENCA),readEncoder,RISING);
}

void loop() {
  delay(1);
  char letter = Serial.read();
  switch (letter){
    case ('x'):
    target_speed = 0.001;
    direction_input = -1;
          break;  
    case ('t'):
        target_speed = 70;
        direction_input = -1;
      break; 
    case ('a'):
        target_speed = 20;
        direction_input = -1;
      break;   
  }

  // read the position in an atomic block
  // to avoid potential misreads
  int pos = 0;
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE){
    pos = pos_i;
    
  }
  Serial.println(pos);
  /*
  if (pos >= 0.70*setpos){
    target_speed = 20;
  }
  if (pos >= setpos){
    target_speed = 0;
  }
  */
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

  // Set a target
  float vt = target_speed;

  // Compute the control signal u
  float kp = 1;
  float ki = 10;
  float e = vt-v1Filt;
  eintegral = eintegral + e*deltaT;
  
  float u = kp*e + ki*eintegral;

  // Set the motor speed and direction
  //receieve input speed (target speed) and distance (speed * time), move to that, ideally receive progress (how far are you from reaching the target distance), accept a stop command 

  int dir = direction_input;
  /*
  if (u<0){
    dir = -1;
  }
  */

  int pwr = (int) fabs(u);
  if(pwr > 255){
    pwr = 255;
    
  }
  
  setMotor(dir,pwr,PWM,IN1,IN2);

    delay(1);
  Serial.print(vt);
  Serial.print(" ");
  Serial.print(v1Filt);
  Serial.println();
  delay(1);
}

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
    increment = -1;
  }
  pos_i = pos_i + increment;

}
