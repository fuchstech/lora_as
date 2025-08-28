#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  pinMode(8, OUTPUT);
  digitalWrite(8, LOW); // Başlangıçta kapalı

  Serial.println("LoRa Receiver Başladı...");
}

void loop() {
  if (mySerial.available()) {
    char c = mySerial.read();
    Serial.print("Gelen veri: ");
    Serial.println(c);

    if (c == 'a') {
      digitalWrite(8, HIGH);
      Serial.println("Pin 8: HIGH (Açık)");
    } else if (c == 'b') {
      digitalWrite(8, LOW);
      Serial.println("Pin 8: LOW (Kapalı)");
    }
  }

  if (Serial.available()) {
    char d = Serial.read();
    mySerial.write(d);
  }
}
