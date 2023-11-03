int FL_enA = 9;
int FL_in1 = 8;
int FL_in2 = 10;
int BL_enB = 11;
int BL_in3 = 12;
int BL_in4 = 13;
int FR_enA = 5;
int FR_in1 = 6;
int FR_in2 = 7;
int BR_enB = 3;
int BR_in3 = 4;
int BR_in4 = 2;
int speed_fwd = 100;
int speed_rot = 100;
int speed_lat = 130;

void setup()
{
  Serial.begin(9600);
// set all the motor control pins to outputs
pinMode(FL_enA, OUTPUT);
pinMode(FL_in1, OUTPUT);
pinMode(FL_in2, OUTPUT);
pinMode(BL_enB, OUTPUT);
pinMode(BL_in3, OUTPUT);
pinMode(BL_in4, OUTPUT);
pinMode(FR_enA, OUTPUT);
pinMode(FR_in1, OUTPUT);
pinMode(FR_in2, OUTPUT);
pinMode(BR_enB, OUTPUT);
pinMode(BR_in3, OUTPUT);
pinMode(BR_in4, OUTPUT);
}

void loop()
{
  if ( Serial.available() ) {
    char cmd = Serial.read();
    Serial.println(cmd);
    switch ( cmd ) {
      case 'w':
        move_forward();
        break;
      
      case 's':
        move_backward();
        break;
      
      case 'a':
        move_left();
        break;
      
      case 'd':
        move_right();
        break;
      
      case 'q':
        turn_ccw();
        break;
      
      case 'e':
        turn_cw();
        break;
      
      default:
        break;
    }
  }

}

void stop(){
analogWrite(FL_enA, 0);
analogWrite(BL_enB, 0);
analogWrite(FR_enA, 0);
analogWrite(BR_enB, 0);
}



void FL_backward(int speed){
analogWrite(FL_enA, speed);
digitalWrite(FL_in1, HIGH); 
digitalWrite(FL_in2, LOW);
}

void FL_forward(int speed){
analogWrite(FL_enA, speed);
digitalWrite(FL_in1, LOW); 
digitalWrite(FL_in2, HIGH);
}

void BL_backward(int speed){
analogWrite(BL_enB, speed);
digitalWrite(BL_in3, LOW); 
digitalWrite(BL_in4, HIGH);
}

void BL_forward(int speed){
analogWrite(BL_enB, speed);
digitalWrite(BL_in3, HIGH); 
digitalWrite(BL_in4, LOW);
}

void FR_backward(int speed){
analogWrite(FR_enA, speed);
digitalWrite(FR_in1, LOW); 
digitalWrite(FR_in2, HIGH);
}

void FR_forward(int speed){
analogWrite(FR_enA, speed);
digitalWrite(FR_in1, HIGH); 
digitalWrite(FR_in2, LOW);
}

void BR_backward(int speed){
analogWrite(BR_enB, speed);
digitalWrite(BR_in3, HIGH); 
digitalWrite(BR_in4, LOW);
}

void BR_forward(int speed){
analogWrite(BR_enB, speed);
digitalWrite(BR_in3, LOW); 
digitalWrite(BR_in4, HIGH);
}


void move_forward(){
  FL_forward(speed_fwd);
  FR_forward(speed_fwd);
  BL_forward(speed_fwd);
  BR_forward(speed_fwd);

delay(300);

stop();
}


void move_backward(){
  BL_backward(speed_fwd);
  FL_backward(speed_fwd);
  FR_backward(speed_fwd);
  BR_backward(speed_fwd);

delay(300);

stop();
}

void move_left(){
  FL_backward(speed_lat);
  BL_forward(speed_lat);
  FR_forward(speed_lat);
  BR_backward(speed_lat);
  delay(400);

stop();
}

void move_right(){
  FL_forward(speed_lat);
  BL_backward(speed_lat);
  FR_backward(speed_lat);
  BR_forward(speed_lat);

delay(400);

stop();
}

void turn_ccw(){
  FL_backward(speed_rot);
  BL_backward(speed_rot);
  FR_forward(speed_rot);
  BR_forward(speed_rot);

delay(200);

stop();
}


void turn_cw(){
  FL_forward(speed_rot);
  BL_forward(speed_rot);
  FR_backward(speed_rot);
  BR_backward(speed_rot);

delay(200);

stop();
}