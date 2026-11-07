"""Ortam değişkenlerinden okunan ayarlar (docker-compose.yml ve .env dosyasından gelir)."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://sulama:sulama123@localhost:5432/sulama")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
IMAGE_DIR = os.getenv("IMAGE_DIR", "./images")
POMPA_DEBI_ML_DK = float(os.getenv("POMPA_DEBI_ML_DK", "1000"))

# MQTT konu (topic) adları. ESP32 yazılımındaki adlarla AYNI olmalıdır.
KONU_TELEMETRI = "sulama/telemetri"          # ESP32 -> sunucu : sensör ölçümleri
KONU_OLAY = "sulama/olay"                    # ESP32 -> sunucu : biten sulama bilgisi
KONU_KOMUT = "sulama/komut"                  # sunucu -> ESP32 : manuel sulama / mod değişimi
KONU_BITKI_INDEKSI = "sulama/bitki_indeksi"  # sunucu -> ESP32 : görüntüden hesaplanan yeşil oran

# Deneydeki saksılar (id -> toprak türü)
SAKSILAR = {1: "kumlu", 2: "killi", 3: "tinli"}
