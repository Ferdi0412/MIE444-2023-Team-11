#include <SoftwareSerial.h>

/* == Motor Communication Stuff == */
#define ULTRASONIC_BUFFER_LEN 128
char ultrasonic_buffer[128];

#define MOTOR_BUFFER_LEN 128
#define M_CMD_DATA 9
char motor_buffer[MOTOR_BUFFER_LEN];

void forward_motor_move( Stream *bt_com, Stream *motor_com ) {
  if ( bt_com->available() < M_CMD_DATA )
    return;
  motor_buffer[0] = 'M';
  bt_com->readBytes( &(motor_buffer[1]), M_CMD_DATA );
  motor_com->write( motor_buffer, M_CMD_DATA + 1 );
}

void forward_motor_reply( Stream *motor_com, Stream *bt_com ) {
  unsigned int bytes_to_send = motor_com->available();
  if ( bytes_to_send > MOTOR_BUFFER_LEN )
    bytes_to_send = MOTOR_BUFFER_LEN;

  if ( bytes_to_send == 0 )
    return;

  motor_com->readBytes(motor_buffer, bytes_to_send);

  bt_com->write(motor_buffer, bytes_to_send);
}

void set_motor_id(Stream *motor_com, char motor_id) {
  motor_buffer[0] = 'X';
  motor_buffer[1] = motor_id;
  motor_com->write(motor_buffer, 2);
}

void* get_motor_com ( char motor_id ) {
  switch ( motor_id ) {
    case 0:
      return (void*) &Serial;

    case 1:
      return (void*) &Serial1;

    case 2:
      return (void*) &Serial2;

    case 3:
      return (void*) &Serial3;

    default:
      return NULL;
  }
}

/* == PIN DEFNS == */
int flsensorTrig = 9;
int frsensorTrig = 10;
int rrsensorTrig = 11;
int bbsensorTrig = 12;
int llsensorTrig = 8;
int flsensorEcho = A1;
int frsensorEcho = A2;
int rrsensorEcho = A3;
int bbsensorEcho = A4;
int llsensorEcho = A0;

//int frontCheck = 0;

unsigned int time[7];
int distance[7];

SoftwareSerial espSerial (A8/*rx*/, A9/*tx*/);

// To allow for string-type handling...

void setup() {
  time[6] = 0;
  distance[6] = 0;

  // put your setup code here, to run once:
  espSerial.begin(9600);
  Serial.begin(9600);
  set_motor_id(&Serial, 0);
  Serial1.begin(9600);
  set_motor_id(&Serial1, 1);
  Serial2.begin(9600);
  set_motor_id(&Serial2, 2);
  Serial3.begin(9600);
  set_motor_id(&Serial3, 3);

  pinMode(flsensorTrig, OUTPUT);
  pinMode(frsensorTrig, OUTPUT);
  pinMode(rrsensorTrig, OUTPUT);
  pinMode(bbsensorTrig, OUTPUT);
  pinMode(llsensorTrig, OUTPUT);
  pinMode(flsensorEcho, INPUT);
  pinMode(frsensorEcho, INPUT);
  pinMode(rrsensorEcho, INPUT);
  pinMode(bbsensorEcho, INPUT);
  pinMode(llsensorEcho, INPUT);
}
  void loop() {
   //put your main code here, to run repeatedly:
  time[1] = SensorPulseDuration(frsensorTrig, frsensorEcho);
  delay(10);
  time[2] = SensorPulseDuration(rrsensorTrig, rrsensorEcho);
  delay(10);
  time[3] = SensorPulseDuration(bbsensorTrig, bbsensorEcho);
  delay(10);
  time[4] = SensorPulseDuration(llsensorTrig, llsensorEcho);
  delay(10);
  time[0] = SensorPulseDuration(flsensorTrig, flsensorEcho);

  distance[0] = time[0]*0.034*0.5;
  distance[1] = time[1]*0.034*0.5;
  distance[2] = time[2]*0.034*0.5;
  distance[3] = time[3]*0.034*0.5;
  distance[4] = time[4]*0.034*0.5;
  //dt = test*0.034*0.5;

  // Serial.print("front left: ");
  // Serial.println(distance[0]);

  // Serial.print("front right: ");
  // Serial.println(distance[1]);

  // Serial.print("left: ");
  // Serial.println(distance[4]);

  // Serial.print("right: ");
  // Serial.println(distance[2]);

  // Serial.print("back: ");
  // Serial.println(distance[3]);

  //if(Serial.available()){
  //  if(Serial.read()=='a'){
  //  Serial1.write('b');
  //  Serial.write('b');
  //  }
  //}
  while ( espSerial.available() ) {
    char motor_id; Stream *target_com = NULL;
    char cmd = espSerial.read();
    switch ( cmd ) {
      /* Reply to Ultrasonic reading request. */
      case 'U':
        Serial.write('U');
        Serial.write((char*) distance, sizeof(unsigned int) * 6);
        break;

      /* Forward Motor commands */
      case 'M':
        // Get character, but keep in Serial buffer...
        motor_id = espSerial.peek();
        if ( (target_com = (Stream*) get_motor_com(motor_id)) != NULL ) {
          forward_motor_move(&espSerial, target_com);
        }
        break;

      /* Stop motor command */
      case 'S':
        Serial.write('S');
        Serial1.write('S');
        Serial2.write('S');
        Serial3.write('S');
        break;

      case 'P':
        motor_id = espSerial.peek();
        if ( (target_com = (Stream*) get_motor_com(motor_id)) != NULL ) {
          target_com->write('P');
        }
        break;

      case 'A':
        motor_id = espSerial.peek();
        if ( (target_com = (Stream*) get_motor_com(motor_id)) != NULL ) {
          target_com->write('A');
        }
        break;

      case 'X':
        set_motor_id(&Serial, 0);
        set_motor_id(&Serial1, 1);
        set_motor_id(&Serial2, 2);
        set_motor_id(&Serial3, 3);
        break;



      default:
        // Do nothing with an invalid character...
        break;

    }
  }
}

unsigned int SensorPulseDuration(int trigPin,int echoPin){
unsigned int duration = 0;
digitalWrite(trigPin, LOW);
delayMicroseconds(2);
digitalWrite(trigPin, HIGH);
delayMicroseconds(10);
digitalWrite(trigPin, LOW);
duration = pulseIn(echoPin, HIGH, 30000);
return duration;
}

void write_to_motor(char id) {
	switch (id) {
		case '1':
			//write(Serial);
      break;
    case '2':
      write(Serial1);
      break;
    case '3':
      write(Serial2);
      break;
    case '4':
      write(Serial3);
      break;
  }
}

void write(Stream &s){
  s.write('M');
        for (int i = 0; i < 8; i ++ ) {
    		s.write(espSerial.read());
        //Serial.write(espSerial.read());
        }
}
