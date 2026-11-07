// Donanım bağlantıları ve ayarlar. Devre kurulduktan sonra buradaki değerleri kontrol edin.
#pragma once

#define SAKSI_SAYISI 3   // 1: kumlu, 2: killi, 3: tinli

// ---- Toprak nem sensörleri (Capacitive Soil Moisture V2.0) ----
// Sadece ADC1 pinleri kullanılmalı (ADC2 pinleri WiFi açıkken çalışmaz).
const int NEM_PINLERI[SAKSI_SAYISI] = {32, 33, 34};
// Kalibrasyon: sensör havadayken (KURU) ve suya batırılmışken (ISLAK) okunan ham değerler.
// GÖREV (Öğrenci A): Her sensör için ölçüp güncelleyin.
const int NEM_KURU[SAKSI_SAYISI]  = {3000, 3000, 3000};
const int NEM_ISLAK[SAKSI_SAYISI] = {1300, 1300, 1300};

// ---- DHT21 (AM2301) sıcaklık / nem sensörü ----
#define DHT_PIN 4

// ---- Röle kartı -> 12V solenoid vanalar ----
const int VANA_PINLERI[SAKSI_SAYISI] = {25, 26, 27};
#define ROLE_AKTIF LOW     // Çoğu röle kartı LOW ile çeker. Sizinki HIGH ile çekiyorsa değiştirin.

// ---- HW-039 (BTS7960) motor sürücü -> 12V pompa ----
#define POMPA_RPWM 18      // hız (PWM)
#define POMPA_LPWM 19      // ters yön, hep 0
#define POMPA_EN   21      // R_EN ve L_EN birlikte bu pine
#define POMPA_PWM_KANAL 0
#define POMPA_PWM_FREKANS 20000
// Açık vana sayısına göre pompa hızı (0-255). İndeks = açık vana sayısı.
// GÖREV (Öğrenci A): Deneyle belirleyin.
const int POMPA_HIZI[SAKSI_SAYISI + 1] = {0, 150, 200, 255};

// ---- Su miktarı ----
// Tek vana açıkken saksıya giden su (ml / saniye). Kalibrasyon deneyiyle belirlenecek.
#define DEBI_ML_SN 16.0f

// ---- Zamanlama ----
#define OLCUM_ARALIGI_MS   60000UL  // Her 60 sn ölç ve gönder
#define MAKS_SULAMA_SN     60       // Güvenlik: bir vana en fazla bu kadar açık kalır
#define SULAMA_SONRASI_BEKLEME_DK 30  // Su toprağa yayılsın diye iki otomatik sulama arası en az süre
