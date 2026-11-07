// Akıllı Sulama Sistemi - Ana kontrol kartı (ESP32)
//
// Görevleri:
//  1. Toprak nem sensörlerini ve DHT21'i okumak
//  2. Ölçümleri MQTT ile sunucuya (Docker'daki Mosquitto) göndermek
//  3. Otomatik modda yapay zekâ modeline (model.h) sorup gerekirse sulamak
//  4. Web arayüzünden gelen manuel sulama / mod komutlarını uygulamak
//  5. Açık vana sayısına göre pompa hızını ayarlamak
//
// MQTT konuları ve mesaj biçimleri: PROJE_PLANI.md -> "MQTT mesaj sözleşmesi"

#include <Arduino.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <PubSubClient.h>
#include <WiFi.h>

#include "config.h"
#include "model.h"
#include "secrets.h"  // secrets.example.h dosyasını kopyalayıp oluşturun

#define KONU_TELEMETRI "sulama/telemetri"
#define KONU_OLAY "sulama/olay"
#define KONU_KOMUT "sulama/komut"
#define KONU_BITKI_INDEKSI "sulama/bitki_indeksi"

WiFiClient wifiIstemci;
PubSubClient mqtt(wifiIstemci);
DHT dht(DHT_PIN, DHT21);

struct Saksi {
  float nem = 0;               // %
  int ham = 0;                 // ADC ham değeri
  float yesilOran = 0;         // sunucudan gelen görüntü analizi sonucu
  bool vanaAcik = false;
  unsigned long vanaAcilis = 0;
  unsigned long vanaKapanis = 0;  // millis() zamanı
  unsigned long sonSulama = 0;    // 0 = hiç sulanmadı
  const char *kaynak = "";
};

Saksi saksilar[SAKSI_SAYISI];
bool otomatikMod = true;
float sicaklik = NAN, havaNem = NAN;
unsigned long sonOlcum = 0;

// ------------------------------------------------------------------ Pompa ve vanalar

int acikVanaSayisi() {
  int n = 0;
  for (auto &s : saksilar) n += s.vanaAcik;
  return n;
}

void pompaGuncelle() {
  ledcWrite(POMPA_PWM_KANAL, POMPA_HIZI[acikVanaSayisi()]);
}

void sulamayiBaslat(int i, float sureSn, const char *kaynak) {
  if (saksilar[i].vanaAcik) return;
  sureSn = constrain(sureSn, 1, MAKS_SULAMA_SN);
  Saksi &s = saksilar[i];
  s.vanaAcik = true;
  s.vanaAcilis = millis();
  s.vanaKapanis = millis() + (unsigned long)(sureSn * 1000);
  s.kaynak = kaynak;
  digitalWrite(VANA_PINLERI[i], ROLE_AKTIF);  // önce vana açılır
  pompaGuncelle();                             // sonra pompa hızlanır
  Serial.printf("Saksı %d sulanıyor: %.1f sn (%s)\n", i + 1, sureSn, kaynak);
}

void sulamayiBitir(int i) {
  Saksi &s = saksilar[i];
  s.vanaAcik = false;
  pompaGuncelle();                              // önce pompa yavaşlar/durur
  digitalWrite(VANA_PINLERI[i], !ROLE_AKTIF);   // sonra vana kapanır
  s.sonSulama = millis();

  float sure = (millis() - s.vanaAcilis) / 1000.0f;
  JsonDocument doc;
  doc["saksi"] = i + 1;
  doc["sure_sn"] = sure;
  doc["su_ml"] = sure * DEBI_ML_SN;
  doc["kaynak"] = s.kaynak;
  char tampon[160];
  serializeJson(doc, tampon);
  mqtt.publish(KONU_OLAY, tampon);
  Serial.printf("Saksı %d sulama bitti (%.1f sn)\n", i + 1, sure);
}

void vanalariKontrolEt() {
  for (int i = 0; i < SAKSI_SAYISI; i++) {
    if (saksilar[i].vanaAcik && (long)(millis() - saksilar[i].vanaKapanis) >= 0) sulamayiBitir(i);
  }
}

// ------------------------------------------------------------------ Sensörler

void sensorleriOku() {
  for (int i = 0; i < SAKSI_SAYISI; i++) {
    long toplam = 0;
    for (int k = 0; k < 10; k++) {  // gürültüyü azaltmak için 10 ölçümün ortalaması
      toplam += analogRead(NEM_PINLERI[i]);
      delay(5);
    }
    int ham = toplam / 10;
    saksilar[i].ham = ham;
    saksilar[i].nem = constrain(
        (float)(NEM_KURU[i] - ham) * 100.0f / (NEM_KURU[i] - NEM_ISLAK[i]), 0.0f, 100.0f);
  }
  float t = dht.readTemperature(), h = dht.readHumidity();
  if (!isnan(t)) sicaklik = t;  // okuma başarısızsa son geçerli değer kalır
  if (!isnan(h)) havaNem = h;
}

void telemetriGonder() {
  JsonDocument doc;
  doc["cihaz"] = "esp32-ana";
  if (!isnan(sicaklik)) doc["sicaklik"] = sicaklik;
  if (!isnan(havaNem)) doc["hava_nem"] = havaNem;
  JsonArray dizi = doc["saksilar"].to<JsonArray>();
  for (int i = 0; i < SAKSI_SAYISI; i++) {
    JsonObject o = dizi.add<JsonObject>();
    o["saksi"] = i + 1;
    o["toprak_nem"] = saksilar[i].nem;
    o["ham"] = saksilar[i].ham;
    o["vana"] = saksilar[i].vanaAcik;
  }
  char tampon[512];
  serializeJson(doc, tampon);
  mqtt.publish(KONU_TELEMETRI, tampon);
}

// ------------------------------------------------------------------ Yapay zekâ kararı

// Girdi sırası ml/src/ozellikler.py içindeki OZELLIKLER listesiyle AYNI olmalıdır.
void modelGirdisiHazirla(int i, float *x) {
  const Saksi &s = saksilar[i];
  x[0] = s.nem;
  x[1] = isnan(sicaklik) ? 24.0f : sicaklik;
  x[2] = isnan(havaNem) ? 50.0f : havaNem;
  x[3] = (float)i;  // saksı sırası = toprak kodu (0 kumlu, 1 killi, 2 tinli)
  x[4] = s.yesilOran;
  x[5] = s.sonSulama == 0 ? 1440.0f : min(1440.0f, (millis() - s.sonSulama) / 60000.0f);
}

void otomatikKarar() {
  for (int i = 0; i < SAKSI_SAYISI; i++) {
    Saksi &s = saksilar[i];
    if (s.vanaAcik) continue;
    if (s.sonSulama != 0 && millis() - s.sonSulama < SULAMA_SONRASI_BEKLEME_DK * 60000UL) continue;

    float x[MODEL_OZELLIK_SAYISI];
    modelGirdisiHazirla(i, x);
    if (model_sulama_gerekli(x)) {
      float ml = model_su_ml(x);
      sulamayiBaslat(i, ml / DEBI_ML_SN, MODEL_EGITILMIS ? "model" : "kural");
    }
  }
}

// ------------------------------------------------------------------ MQTT

void mesajGeldi(char *konu, byte *veri, unsigned int uzunluk) {
  JsonDocument doc;
  if (deserializeJson(doc, veri, uzunluk)) return;  // bozuk JSON'u yok say

  if (strcmp(konu, KONU_KOMUT) == 0) {
    const char *islem = doc["islem"] | "";
    if (strcmp(islem, "mod") == 0) {
      otomatikMod = strcmp(doc["mod"] | "otomatik", "otomatik") == 0;
      Serial.printf("Mod: %s\n", otomatikMod ? "otomatik" : "manuel");
    } else if (strcmp(islem, "sula") == 0) {
      int saksi = doc["saksi"] | 0;
      if (saksi >= 1 && saksi <= SAKSI_SAYISI) sulamayiBaslat(saksi - 1, doc["sure_sn"] | 5.0f, "manuel");
    }
  } else if (strcmp(konu, KONU_BITKI_INDEKSI) == 0) {
    int saksi = doc["saksi"] | 0;
    if (saksi >= 1 && saksi <= SAKSI_SAYISI) saksilar[saksi - 1].yesilOran = doc["yesil_oran"] | 0.0f;
  }
}

void baglantilariKoru() {
  if (WiFi.status() != WL_CONNECTED) return;  // WiFi kütüphanesi kendisi yeniden bağlanır
  if (mqtt.connected()) return;
  static unsigned long sonDeneme = 0;
  if (millis() - sonDeneme < 5000) return;
  sonDeneme = millis();
  Serial.print("MQTT'ye bağlanılıyor... ");
  if (mqtt.connect("esp32-ana")) {
    Serial.println("tamam");
    mqtt.subscribe(KONU_KOMUT);
    mqtt.subscribe(KONU_BITKI_INDEKSI);
  } else {
    Serial.printf("başarısız (kod %d)\n", mqtt.state());
  }
}

// ------------------------------------------------------------------ Ana program

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < SAKSI_SAYISI; i++) {
    pinMode(VANA_PINLERI[i], OUTPUT);
    digitalWrite(VANA_PINLERI[i], !ROLE_AKTIF);  // başlangıçta tüm vanalar kapalı
  }
  pinMode(POMPA_EN, OUTPUT);
  pinMode(POMPA_LPWM, OUTPUT);
  digitalWrite(POMPA_EN, HIGH);
  digitalWrite(POMPA_LPWM, LOW);
  ledcSetup(POMPA_PWM_KANAL, POMPA_PWM_FREKANS, 8);
  ledcAttachPin(POMPA_RPWM, POMPA_PWM_KANAL);
  pompaGuncelle();

  analogReadResolution(12);
  dht.begin();

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_SIFRE);
  Serial.print("WiFi'ye bağlanılıyor");
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nIP: %s\n", WiFi.localIP().toString().c_str());

  mqtt.setServer(MQTT_SUNUCU, MQTT_PORT);
  mqtt.setBufferSize(1024);
  mqtt.setCallback(mesajGeldi);
}

void loop() {
  baglantilariKoru();
  mqtt.loop();
  vanalariKontrolEt();  // sulama süresi dolan vanaları kapat (bağlantı olmasa da çalışır)

  if (sonOlcum == 0 || millis() - sonOlcum >= OLCUM_ARALIGI_MS) {
    sonOlcum = millis();
    sensorleriOku();
    if (mqtt.connected()) telemetriGonder();
    if (otomatikMod) otomatikKarar();  // sunucuya bağlı olmasa da sulamaya devam eder
  }
}
