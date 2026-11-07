"""Marul fotoğrafından bitki durumunu çıkaran basit görüntü analizi.

Şu anki yöntem: HSV renk uzayında "yeşil" sayılan piksellerin oranı.
Bu oran bitkinin büyüklüğü / yaprak alanı hakkında fikir verir ve
makine öğrenmesi modeline ek bir özellik (feature) olarak girer.

GÖREV (Öğrenci C): Eşik değerlerini gerçek fotoğraflarla ayarlayın,
gerekirse solgunluk / sararma gibi ek göstergeler ekleyin.
"""
import numpy as np
from PIL import Image

# HSV eşikleri (Pillow'da H, S, V değerleri 0-255 aralığındadır)
YESIL_H_MIN, YESIL_H_MAX = 35, 120
YESIL_S_MIN = 60
YESIL_V_MIN = 40


def yesil_oran_hesapla(dosya_yolu: str) -> float:
    hsv = np.asarray(Image.open(dosya_yolu).convert("HSV"))
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    maske = (h >= YESIL_H_MIN) & (h <= YESIL_H_MAX) & (s >= YESIL_S_MIN) & (v >= YESIL_V_MIN)
    return float(maske.mean())
