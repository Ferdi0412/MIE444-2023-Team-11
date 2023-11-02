/*
We are using 1 interupt to track 2 pins...

Interrupt on enc_A

enc_B leads, this means that:
- If enc_A RISES and enc_B is HIGH, define as: CLOCKWISE
- If enc_A RISES and enc_B is LOW, define as: COUNTER-CLOCKWISE
- If enc_A FALLS and enc_B is LOW, define as: CLOCKWISE
- If enc_A FALLS and enc_B is LOW, define as: COUNTER-CLOCKWISE

*/
#define INPUT 1
#define OUTPUT 1
#define HIGH 1
#define LOW 0
# define CHANGE 0

int digitalWrite( int some_pin, int val );
int digitalRead( int some_pin );
int pinMode(int a, int B);
void attachInterrupt(int a, void* b, int c);
int digitalPinToInterrupt(int a);

// Add this to the top of the file

# define FACTOR_FWD 50 /* Conversion for forward distance to encoder rotations... */

class Motor {
    private:
        int enc_A;
        int enc_B;

        int dir_A;
        int dir_B;

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
            digitalWrite(dir_B, LOW);
            digitalWrite(dir_A, HIGH);
        }

        // Jog backward
        void start_bwd() {
            digitalWrite(dir_A, LOW);
            digitalWrite(dir_B, HIGH);
        }

    public:
        // Constructor
        Motor( int enc_A_, int enc_B_, int dir_A_, int dir_B_) : enc_A(enc_A_), enc_B(enc_B_), dir_A(dir_A_), dir_B(dir_B_), pos(0), target_pos(0) {
            // Encoder inputs
            pinMode(enc_A, INPUT);
            pinMode(enc_B, INPUT);

            // Motor direction outputs
            pinMode(dir_A, OUTPUT);
            pinMode(dir_B, OUTPUT);

            // Set enc_A interrupt
            attachInterrupt( digitalPinToInterrupt(enc_A), (void *) interrupt, CHANGE );
        }

        // Callback for interrupt
        int interrupt() {
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
            digitalWrite(dir_A, HIGH);
            digitalWrite(dir_B, HIGH);
        }

        // Stop/idle the motor
        void stop() {
            digitalWrite(dir_A, LOW);
            digitalWrite(dir_B, LOW);
        }

        // Move motor
        int forward( float distance ) {
            target_pos = pos + static_cast<long>(distance * FACTOR_FWD);
            is_fwd = (int) (distance > 0);
        }

        // Progress along motion
        float progress() {
            return 100 * ( pos - start_pos ) / ( target_pos - start_pos );
        }
};


// Add this to the bottom of the file

int generic_motor_callback( struct motor_encoder& encoder ) {
    // Update motor "position"
    if ( clockwise( encoder ) )
        encoder->pos ++;
    else
        encoder->pos --;
}


int clockwise(struct motor_encoder& encoder) {
    if ( digitalRead( encoder->enc_A ) ) {
        // enc_A RISES
        if ( digitalRead( encoder->enc_B ) )
            // CLOCKWISE
            return 1;
        else
            // COUNTER-CLOCKWISE
            return 0;
    }
    else {
        // enc_A FALLS
        if ( digitalRead( encoder->enc_B ) )
            // COUNTER-CLOCKWISE
            return 0;
        else
            // CLOCKWISE
            return 1;
    }
}
