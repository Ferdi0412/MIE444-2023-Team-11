#define enA 5
#define pin1 18
#define pin2 19

#define pwmChannel 0

void setup() {
  // put your setup code here, to run once:
  ledcSetup(pwmChannel, 490, 8);
  ledcAttachPin(enA, pwmChannel);

  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);

  ledcWrite(enA, 500);
  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:

}
