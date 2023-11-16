#include <SoftwareSerial.h>

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

SoftwareSerial motorSerial (2/*rx*/, 3/*tx*/);

// To allow for string-type handling...

void setup() {
  time[6] = 0;
  distance[6] = 0;

  // put your setup code here, to run once:
  Serial.begin(9600);
  motorSerial.begin(9600);
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

  if ( Serial.available() ) {
    char cmd = Serial.read();
    switch ( cmd ) {
      case 'u':
        Serial.print(String(distance[0]));
        Serial.print(";");
        Serial.print(String(distance[1]));
        Serial.print(";");
        Serial.print(String(distance[2]));
        Serial.print(";");
        Serial.print(String(distance[3]));
        Serial.print(";");
        Serial.println(String(distance[4]));
        break;
      
      default:
        motorSerial.write(cmd);
        break;

    }
  }

  delay(100);
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