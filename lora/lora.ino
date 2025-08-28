#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX

const int buttonPin = 8;
bool buttonState = HIGH;        // Şu anki buton durumu
bool lastButtonState = HIGH;    // Önceki döngüdeki buton durumu
unsigned long lastDebounceTime = 0;  
unsigned long debounceDelay = 50; // 50 ms debounce süresi

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);
  Serial.println("LoRa Verici Başladı...");
}

void loop() {
  int reading = digitalRead(buttonPin);

  // Buton durumu değişmişse zaman damgası al
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  // Değişiklik debounce süresince sabit kaldıysa, buton durumu değişti
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;

      // Butona basıldıysa (LOW)
      if (buttonState == LOW) {
        mySerial.write('a');
        Serial.println("Gönderildi: a");
      }
      // Buton bırakıldıysa (HIGH)
      else {
        mySerial.write('b');
        Serial.println("Gönderildi: b");
      }
    }
  }

  lastButtonState = reading;

  // (İsteğe bağlı) LoRa'dan geleni yaz
  if (mySerial.available()) {
    char c = mySerial.read();
    Serial.write(c);
  }

  // (İsteğe bağlı) Serial üzerinden yazılanı LoRa'ya gönder
  if (Serial.available()) {
    char d = Serial.read();
    mySerial.write(d);
  }
}
