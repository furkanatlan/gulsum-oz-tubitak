// Akıllı Sulama Sistemi - ESP32-CAM
// Belirli aralıklarla marulun fotoğrafını çeker ve HTTP ile backend'e yükler:
//   POST {SUNUCU_ADRESI}/api/goruntuler/yukle?saksi_id={SAKSI_ID}   (Content-Type: image/jpeg)
// Sunucu fotoğraftaki yeşil oranı hesaplar ve MQTT ile ana ESP32'ye iletir.

#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFi.h>

#include "esp_camera.h"
#include "secrets.h"  // secrets.example.h dosyasını kopyalayıp oluşturun

#define FOTO_ARALIGI_MS (30UL * 60 * 1000)  // 30 dakikada bir
#define FLAS_PIN 4                           // dahili LED (gerekirse kullanın)

// AI Thinker ESP32-CAM pin bağlantıları
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

unsigned long sonFoto = 0;

bool kamerayiBaslat() {
  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = Y2_GPIO_NUM;
  c.pin_d1 = Y3_GPIO_NUM;
  c.pin_d2 = Y4_GPIO_NUM;
  c.pin_d3 = Y5_GPIO_NUM;
  c.pin_d4 = Y6_GPIO_NUM;
  c.pin_d5 = Y7_GPIO_NUM;
  c.pin_d6 = Y8_GPIO_NUM;
  c.pin_d7 = Y9_GPIO_NUM;
  c.pin_xclk = XCLK_GPIO_NUM;
  c.pin_pclk = PCLK_GPIO_NUM;
  c.pin_vsync = VSYNC_GPIO_NUM;
  c.pin_href = HREF_GPIO_NUM;
  c.pin_sccb_sda = SIOD_GPIO_NUM;
  c.pin_sccb_scl = SIOC_GPIO_NUM;
  c.pin_pwdn = PWDN_GPIO_NUM;
  c.pin_reset = RESET_GPIO_NUM;
  c.xclk_freq_hz = 20000000;
  c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size = FRAMESIZE_SVGA;  // 800x600
  c.jpeg_quality = 12;            // 0-63, küçük sayı = daha kaliteli
  c.fb_count = 1;
  c.fb_location = CAMERA_FB_IN_PSRAM;
  c.grab_mode = CAMERA_GRAB_LATEST;
  return esp_camera_init(&c) == ESP_OK;
}

void fotografGonder() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Fotoğraf çekilemedi");
    return;
  }
  HTTPClient http;
  String adres = String(SUNUCU_ADRESI) + "/api/goruntuler/yukle?saksi_id=" + SAKSI_ID;
  http.begin(adres);
  http.addHeader("Content-Type", "image/jpeg");
  int kod = http.POST(fb->buf, fb->len);
  Serial.printf("Fotoğraf gönderildi (%u bayt) -> HTTP %d %s\n", fb->len, kod, http.getString().c_str());
  http.end();
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);
  pinMode(FLAS_PIN, OUTPUT);
  digitalWrite(FLAS_PIN, LOW);

  if (!kamerayiBaslat()) {
    Serial.println("Kamera başlatılamadı! 10 sn sonra yeniden başlatılıyor.");
    delay(10000);
    ESP.restart();
  }

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_SIFRE);
  Serial.print("WiFi'ye bağlanılıyor");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nIP: %s\n", WiFi.localIP().toString().c_str());
}

void loop() {
  if (sonFoto == 0 || millis() - sonFoto >= FOTO_ARALIGI_MS) {
    sonFoto = millis();
    if (WiFi.status() == WL_CONNECTED) fotografGonder();
  }
  delay(1000);
}
