// BU DOSYA OTOMATİK ÜRETİLDİ (ml/src/egit.py). ELLE DEĞİŞTİRMEYİN.
#pragma once

#define MODEL_OZELLIK_SAYISI 6
#define MODEL_EGITILMIS 1

// Girdi sırası:
//   x[0] = toprak_nem
//   x[1] = sicaklik
//   x[2] = hava_nem
//   x[3] = toprak_kodu
//   x[4] = yesil_oran
//   x[5] = son_sulamadan_dk

// 1 = sulama gerekli, 0 = gerekli değil
static inline int model_sulama_gerekli(const float *x) {
    if (x[0] <= 47.950001f) {
        return 1;
    } else {
        if (x[5] <= 721.500000f) {
            if (x[3] <= 0.500000f) {
                if (x[0] <= 56.950001f) {
                    return 1;
                } else {
                    if (x[2] <= 53.500000f) {
                        return 0;
                    } else {
                        return 1;
                    }
                }
            } else {
                return 0;
            }
        } else {
            return 1;
        }
    }
}

// Verilmesi gereken su miktarı (ml)
static inline float model_su_ml(const float *x) {
    if (x[0] <= 54.350000f) {
        return 133.3f;
    } else {
        if (x[3] <= 0.500000f) {
            return 133.3f;
        } else {
            return 50.0f;
        }
    }
}
