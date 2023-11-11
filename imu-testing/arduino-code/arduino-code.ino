#define OUTPUT_READABLE_ACCELGYRO

/*
Initially using: https://github.com/ElectronicCats/mpu6050/blob/master/examples/MPU6050_raw/MPU6050_raw.ino
*/
#include "I2Cdev.h"
#include "MPU6050.h"

#define LED_ONBOARD 13

#if I2CDEV_IMPLEMENTATION == I2C_ARDUINO_WIRE
  #include "Wire.h"
#endif

MPU6050 imu; // Use MPU6050 imu(0x69); if AD0 not shorted....

int16_t ax, ay, az;
int16_t gx, gy, gz;

int imu_connected;

void setup() {
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin();
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400, true);
  #endif

  // TODO: Change
  Serial.begin(9600);

  imu.initialize();

  imu_connected = imu.testConnection();

  pinMode(LED_ONBOARD, OUTPUT);
}

void write_int16(int16_t value) {
  Serial.write((uint8_t)(value >> 8));
  Serial.write((uint8_t)(value & 0xFF));
}

void loop() {
  imu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  if ( Serial.available() ) {
    char msg = Serial.read();
    switch ( msg ) {
      case 'U': 
        digitalWrite(LED_ONBOARD, HIGH);
        Serial.write('U');
        write_int16(ax);
        write_int16(ay);
        write_int16(az);
        write_int16(gx);
        write_int16(gy);
        write_int16(gz);
        delay(500);
        digitalWrite(LED_ONBOARD, LOW);
    }
  }
  // Serial.println("New line...");
  delay(500);
}