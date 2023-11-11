#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"

MPU6050 imu;

/* Store Gyro/Accel readings */
int16_t ax, ay, az;
int16_t gx, gy, gz;

/* Store "integral" of readings */
unsigned long vx, vy, vz;
unsigned long rx, ry, rz;

/* Store "position" of readings */
unsigned long px, py, pz;

/* Eventually add offsets for callibration */
int16_t ax_offset, ay_offset, az_offset;
int16_t gx_offset, gy_offset, gz_offset;

/* Store timestamp to allow for integration */
unsigned long last_time;
unsigned long temp_time;
unsigned long delta_time;

#define IMU_PIN 34

void setup() {
  // put your setup code here, to run once:
  Wire.begin();

  imu.initialize();

  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  get_values();
  delay(500);
  
}

void get_values() {
  imu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  // temp_time = millis();

  Serial.print("AX: ");
  Serial.print(ax);
  Serial.println("");

  /*

  ax -= ax_offset;
  ay -= ay_offset;
  az -= az_offset;

  gx -= gx_offset;
  gy -= gy_offset;
  gz -= gz_offset;

  */

  // delta_time = temp_time - last_time;

  // vx += ax * delta_time;

}