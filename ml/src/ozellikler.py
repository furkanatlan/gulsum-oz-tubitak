"""Model girdileri (özellikler) ve etiketler.

ÖNEMLİ: OZELLIKLER listesinin SIRASI, ESP32 yazılımında (firmware/esp32-controller/src/main.cpp,
`modelGirdisiHazirla` fonksiyonu) diziye yazılan sırayla AYNI olmalıdır.
"""
import pandas as pd

TOPRAK_KODU = {"kumlu": 0, "killi": 1, "tinli": 2}

OZELLIKLER = [
    "toprak_nem",        # x[0] %
    "sicaklik",          # x[1] °C
    "hava_nem",          # x[2] %
    "toprak_kodu",       # x[3] 0=kumlu 1=killi 2=tinli
    "yesil_oran",        # x[4] 0-1, fotoğraftan
    "son_sulamadan_dk",  # x[5] dakika (en fazla 1440)
]

# Bir ölçümden sonraki UFUK_DK dakika içinde sulama yapıldıysa o ölçüm "sulama gerekli" sayılır.
UFUK_DK = 30


def hazirla(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Ham CSV'den X (özellikler), y_sinif (sulama gerekli mi) ve y_ml (su miktarı) üretir.

    GÖREV (Öğrenci C): Etiketleme yöntemini deney sonuçlarına göre iyileştirin.
    Şu anki yöntem, deney sırasında verilen (kural/manuel) sulama kararlarını taklit eder.
    """
    df = df.dropna(subset=["toprak_nem", "sicaklik", "hava_nem"]).copy()
    df["toprak_kodu"] = df["toprak_turu"].map(TOPRAK_KODU)
    df["yesil_oran"] = df["yesil_oran"].fillna(0.0)
    df["son_sulamadan_dk"] = df["son_sulamadan_dk"].fillna(1440).clip(upper=1440)

    y_sinif = (df["sonraki_sulama_dk"].fillna(1e9) <= UFUK_DK).astype(int)
    y_ml = df["sonraki_sulama_ml"].fillna(0.0)
    return df[OZELLIKLER], y_sinif, y_ml
