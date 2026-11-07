// GEÇİCİ MODEL: Gerçek model eğitilene kadar basit eşik kuralı kullanılır.
// "docker compose exec ml python src/egit.py" komutu bu dosyanın üzerine eğitilmiş modeli yazar.
#pragma once

#define MODEL_OZELLIK_SAYISI 6
#define MODEL_EGITILMIS 0

// Girdi sırası:
//   x[0] = toprak_nem
//   x[1] = sicaklik
//   x[2] = hava_nem
//   x[3] = toprak_kodu (0=kumlu 1=killi 2=tinli)
//   x[4] = yesil_oran
//   x[5] = son_sulamadan_dk

static inline int model_sulama_gerekli(const float *x) {
    return x[0] < 35.0f ? 1 : 0;
}

static inline float model_su_ml(const float *x) {
    (void)x;
    return 150.0f;
}
