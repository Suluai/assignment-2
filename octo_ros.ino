// Assignment #02 - Octoliner + L298N + ROS 2 (serial bridge)
// Sends "S,v0,...,v7" every 100 ms, receives FORWARD / STOP commands.
#include <Wire.h>
#include <Octoliner.h>

Octoliner octoliner;

// ===== MOTOR PINS (L298N) =====
const int ENA = 9;          // PWM speed
const int IN1 = 7;
const int IN2 = 8;
const int motorSpeed = 180; // 0-255

unsigned long lastCmd = 0;
unsigned long lastSend = 0;

void motorOn() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, motorSpeed);
}

void motorOff() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
}

void readCommand() {
  if (Serial.available()) {
    String c = Serial.readStringUntil('\n');
    c.trim();
    if (c == "FORWARD")   { motorOn();  lastCmd = millis(); }
    else if (c == "STOP") { motorOff(); lastCmd = millis(); }
  }
}

void sendSensorData() {     // S,v0,...,v7
  Serial.print("S");
  for (uint8_t i = 0; i < 8; i++) {
    Serial.print(",");
    Serial.print(octoliner.analogRead(i));
  }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  motorOff();               // safe start-up
  octoliner.begin();
  octoliner.setSensitivity(200);
}

void loop() {
  readCommand();
  if (millis() - lastSend >= 100) {
    lastSend = millis();
    sendSensorData();       // about 10 packets per second
  }
  if (millis() - lastCmd > 1000) motorOff();   // failsafe
}
