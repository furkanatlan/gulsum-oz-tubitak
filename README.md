# Yapay Zekâ Destekli Akıllı Sulama Sistemi (TÜBİTAK Projesi)

Marul bitkisinin su ihtiyacını farklı toprak türleri (kumlu, killi, tınlı) ve çevresel koşullara göre belirleyen, sulamayı otomatik yapan sistem.

📋 **Görev dağılımı, geliştirme adımları ve Docker rehberi:** [PROJE_PLANI.md](PROJE_PLANI.md)

## Hızlı başlangıç

Gereksinimler: Git ve Docker Desktop.

```powershell
git clone https://github.com/furkanatlan/gulsum-oz-tubitak.git
cd gulsum-oz-tubitak
copy .env.example .env
docker compose --profile sim up -d --build
```

| Adres | Ne var? |
|---|---|
| http://localhost:5173 | Web arayüzü |
| http://localhost:8000/docs | Backend API belgesi |
| http://localhost:8888 | Jupyter Lab (`--profile ml` ile) |

## Klasörler

| Klasör | İçerik |
|---|---|
| `backend/` | FastAPI sunucu, MQTT köprüsü, PostgreSQL modelleri, görüntü analizi |
| `frontend/` | React (Vite) web arayüzü |
| `simulator/` | Donanım olmadan test için sanal ESP32 |
| `ml/` | Model eğitimi ve ESP32 için C koduna çevirme |
| `firmware/esp32-controller/` | Ana ESP32 yazılımı (PlatformIO) |
| `firmware/esp32-cam/` | ESP32-CAM yazılımı (PlatformIO) |
| `docs/` | Proje tanımı ve deney belgeleri |
