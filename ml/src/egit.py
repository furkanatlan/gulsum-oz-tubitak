"""Modeli eğitir, sonuçları yazdırır ve ESP32 için model.h dosyasını üretir.

Çalıştırma:  docker compose exec ml python src/egit.py
Çıktı:       firmware/esp32-controller/include/model.h
"""
import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text

from c_aktar import header_uret
from ozellikler import OZELLIKLER, hazirla

KOK = Path(__file__).resolve().parent.parent
VERI = KOK / "data" / "veri.csv"
MODEL_KLASORU = KOK / "models"
FIRMWARE_INCLUDE = Path(os.getenv("FIRMWARE_INCLUDE", "/firmware_include"))

# Ağaç derinliği küçük tutulur: ESP32 belleğine sığsın ve aşırı öğrenme (ezber) olmasın.
SINIF_DERINLIK = 5
REGRESYON_DERINLIK = 4


def main():
    X, y_sinif, y_ml = hazirla(pd.read_csv(VERI))
    print(f"Veri: {len(X)} satır, sulama gerekli oranı: {y_sinif.mean():.2%}")

    X_egt, X_tst, ys_egt, ys_tst, ym_egt, ym_tst = train_test_split(
        X, y_sinif, y_ml, test_size=0.2, random_state=42, stratify=y_sinif)

    sinif = DecisionTreeClassifier(max_depth=SINIF_DERINLIK, class_weight="balanced", random_state=42)
    sinif.fit(X_egt, ys_egt)
    print("\n--- Sulama gerekli mi? (test verisi) ---")
    print(classification_report(ys_tst, sinif.predict(X_tst), target_names=["gerekmez", "gerekli"]))
    print(export_text(sinif, feature_names=OZELLIKLER))

    # Su miktarı modeli sadece "sulama gerekli" satırlarla eğitilir
    maske_egt, maske_tst = ys_egt == 1, ys_tst == 1
    reg = DecisionTreeRegressor(max_depth=REGRESYON_DERINLIK, random_state=42)
    reg.fit(X_egt[maske_egt], ym_egt[maske_egt])
    if maske_tst.any():
        hata = mean_absolute_error(ym_tst[maske_tst], reg.predict(X_tst[maske_tst]))
        print(f"--- Su miktarı ortalama mutlak hata: {hata:.1f} ml ---")

    MODEL_KLASORU.mkdir(exist_ok=True)
    joblib.dump({"sinif": sinif, "reg": reg, "ozellikler": OZELLIKLER}, MODEL_KLASORU / "model.joblib")

    FIRMWARE_INCLUDE.mkdir(parents=True, exist_ok=True)
    hedef = FIRMWARE_INCLUDE / "model.h"
    hedef.write_text(header_uret(sinif, reg, OZELLIKLER), encoding="utf-8")
    print(f"\nESP32 model dosyası yazıldı: {hedef}")


if __name__ == "__main__":
    main()
