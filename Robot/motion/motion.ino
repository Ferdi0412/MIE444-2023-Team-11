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
int speed = 100;

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



void FL_backward(){
analogWrite(FL_enA, speed);
digitalWrite(FL_in1, HIGH); 
digitalWrite(FL_in2, LOW);
}

void FL_forward(){
analogWrite(FL_enA, speed);
digitalWrite(FL_in1, LOW); 
digitalWrite(FL_in2, HIGH);
}

void BL_backward(){
analogWrite(BL_enB, speed);
digitalWrite(BL_in3, LOW); 
digitalWrite(BL_in4, HIGH);
}

void BL_forward(){
analogWrite(BL_enB, speed);
digitalWrite(BL_in3, HIGH); 
digitalWrite(BL_in4, LOW);
}

void FR_backward(){
analogWrite(FR_enA, speed);
digitalWrite(FR_in1, LOW); 
digitalWrite(FR_in2, HIGH);
}

void FR_forward(){
analogWrite(FR_enA, speed);
digitalWrite(FR_in1, HIGH); 
digitalWrite(FR_in2, LOW);
}

void BR_backward(){
analogWrite(BR_enB, speed);
digitalWrite(BR_in3, HIGH); 
digitalWrite(BR_in4, LOW);
}

void BR_forward(){
analogWrite(BR_enB, speed);
digitalWrite(BR_in3, LOW); 
digitalWrite(BR_in4, HIGH);
}


void move_forward(){
  FL_forward();
  FR_forward();
  BL_forward();
  BR_forward();

delay(300);

stop();
}


void move_backward(){
  BL_backward();
  FL_backward();
  FR_backward();
  BR_backward();

delay(300);

stop();
}

void move_left(){
  FL_backward();
  BL_forward();
  FR_forward();
  BR_backward();
  delay(800);

stop();
}

void move_right(){
  FL_forward();
  BL_backward();
  FR_backward();
  BR_forward();

delay(800);

stop();
}

void turn_ccw(){
  FL_backward();
  BL_backward();
  FR_forward();
  BR_forward();

delay(200);

stop();
}


void turn_cw(){
  FL_forward();
  BL_forward();
  FR_backward();
  BR_backward();

delay(200);

stop();
}