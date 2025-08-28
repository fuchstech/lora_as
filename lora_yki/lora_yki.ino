#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX

// Buton ayarları
const int buttonPin = 8;
bool buttonState = HIGH;
bool lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);
  Serial.println("LoRa Verici Başladı...");
  Serial.println("Python arayüzünden veya butondan komut bekleniyor.");
}

void loop() {
  // --- BUTON KONTROL KISMI (Röle için) ---
  int reading = digitalRead(buttonPin);

  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == LOW) {
        mySerial.write('a');
        Serial.println("Buton basıldı, röle komutu gönderildi: a");
      } else {
        mySerial.write('b');
        Serial.println("Buton bırakıldı, röle komutu gönderildi: b");
      }
    }
  }
  lastButtonState = reading;

  // --- PYTHON ARAYÜZÜNDEN GELEN VERİYİ GÖNDERME KISMI ---
  // Bilgisayarın seri portundan veri gelip gelmediğini kontrol et
  if (Serial.available() > 0) {
    // Gelen veriyi satır sonu karakterine kadar oku ('\n')
    String dataToSend = Serial.readStringUntil('\n');
    
    // Veriyi LoRa üzerinden gönder
    mySerial.print(dataToSend);
    
    // Bilgi amaçlı bilgisayarın seri portuna da yazdır
    Serial.print("Python'dan alındı, LoRa ile gönderiliyor: ");
    Serial.println(dataToSend);
  }
}