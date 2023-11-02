#define FACTOR_FWD 1

class Motor {
    private:
        int enc_A;
        int enc_B;

        int dir_A;
        int dir_B;
        int enable;

        long pos;
        long target_pos;
        long start_pos;

        int is_fwd;


        // Get direction of last motion
        int direction() {
            /* Returns 1 on CLOCKWISE, -1  on COUNTER-CLOCKWISE */
            // enc_A RISE
            if ( digitalRead( enc_A ) ) {
                // CLOCKWISE
                if ( digitalRead( enc_B ) )
                    return 1;

                // COUNTER-CLOCKWISE
                else
                    return -1;
            }
            // enc_A FALLS
            else {
                // COUNTER-CLOCKWISE
                if ( digitalRead( enc_B ) )
                    return -1;

                // CLOCKWISE
                else
                    return 1;
            }
        }

        // Jog forward
        void start_fwd() {
            digitalWrite(enable, HIGH);
            digitalWrite(dir_B, LOW);
            digitalWrite(dir_A, HIGH);
        }

        // Jog backward
        void start_bwd() {
            digitalWrite(enable, HIGH);
            digitalWrite(dir_A, LOW);
            digitalWrite(dir_B, HIGH);
        }

    public:
        // Constructor
        Motor( int enc_A_, int enc_B_, int dir_A_, int dir_B_, int enable_) : enc_A(enc_A_), enc_B(enc_B_), dir_A(dir_A_), dir_B(dir_B_), enable(enable_), pos(0), target_pos(0) {};
        
        long getPos() {
          return pos;
        }

        void setup () {
            // Encoder inputs
            pinMode(enc_A, INPUT);
            pinMode(enc_B, INPUT);

            // Motor direction outputs
            pinMode(dir_A, OUTPUT);
            pinMode(dir_B, OUTPUT);

            // Enable pin
            pinMode(enable, OUTPUT);
        }

        _attachInterrupt( void *function ) {
          attachInterrupt( digitalPinToInterrupt(enc_A), function, CHANGE );
        }

        // Callback for interrupt
        void interrupt() {
            pos += direction();
            if ( is_fwd && pos >= target_pos ) {
                stop();
            }
            else if ( !is_fwd && pos <= target_pos ) {
                stop();
            }
        }

        // Brake the motor
        void brake() {
            digitalWrite(enable, HIGH);
            digitalWrite(dir_A, HIGH);
            digitalWrite(dir_B, HIGH);
        }

        // Stop/idle the motor
        void stop() {
            digitalWrite(enable, LOW);
            digitalWrite(dir_A, LOW);
            digitalWrite(dir_B, LOW);
        }

        // Move motor
        int forward( float distance ) {
            long next_pos = pos + static_cast<long>(distance * FACTOR_FWD);
            is_fwd = (int) (distance > 0);
            // Ensure no errors in stuff...
            if ( is_fwd && (next_pos < pos) ){
              pos = 0;
              target_pos = pos + static_cast<long>(distance * FACTOR_FWD);
            }
            else if ( !is_fwd && (next_pos > pos) ){
              pos = 0;
              target_pos = pos + static_cast<long>(distance * FACTOR_FWD);
            }
            else
              target_pos = next_pos;
            
            start_pos= pos;
            if ( is_fwd )
              start_fwd();
            else 
              start_bwd();

            Serial.println("Moving....");
            if ( is_fwd )
              Serial.println("Forward...");
            else
              Serial.println("Backwards....");
        }

        // Progress along motion
        float progress() {
            return 100 * ( pos - start_pos ) / ( target_pos - start_pos );
        }
};

Motor motor_1(18, 19, 10, 9, 8);
// Motor motor_2;
// Motor motor_3;
// Motor motor_4;

void interrupt_1() {
  motor_1.interrupt();
}



void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // motor_1.setup();
  // motor_1._attachInterrupt(interrupt_1);
  // motor_1.forward(1000);

  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);

  digitalWrite(8, HIGH);
  digitalWrite(9, LOW);
  digitalWrite(10, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(2000);
  // Serial.println( motor_1.getPos() );
  Serial.println( millis() );
}

