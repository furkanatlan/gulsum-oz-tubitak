"""Sanal ESP32: donanım hazır olmadan sistemi test etmek için sahte sensör verisi üretir.

Gerçek ESP32 ile AYNI MQTT konularını ve mesaj biçimlerini kullanır. Böylece
backend ve web arayüzü, donanım gelmeden önce geliştirilip test edilebilir.

- Her ARALIK_SN saniyede bir telemetri gönderir.
- Toprak nemi zamanla azalır (kumlu toprak en hızlı, killi en yavaş kurur).
- Nem %35'in altına düşünce "kural" ile sular; web'den gelen manuel komutlara da uyar.
"""
import json
import os
import random
import time

import paho.mqtt.client as mqtt

HOST = os.getenv("MQTT_HOST", "localhost")
ARALIK = float(os.getenv("ARALIK_SN", "5"))
DEBI_ML_SN = 1000 / 60

# saksı -> [nem, kuruma hızı (%/adım), sulamada saniye başına nem artışı]
saksilar = {
    1: {"tur": "kumlu", "nem": 55.0, "kuruma": 0.9, "artis": 3.0},
    2: {"tur": "killi", "nem": 60.0, "kuruma": 0.3, "artis": 1.2},
    3: {"tur": "tinli", "nem": 58.0, "kuruma": 0.5, "artis": 2.0},
}
mod = "otomatik"


def sula(client, saksi: int, sure: float, kaynak: str) -> None:
    s = saksilar[saksi]
    s["nem"] = min(90.0, s["nem"] + s["artis"] * sure)
    client.publish("sulama/olay", json.dumps({
        "saksi": saksi, "sure_sn": sure, "su_ml": round(sure * DEBI_ML_SN, 1), "kaynak": kaynak}))
    print(f"Saksı {saksi} sulandı ({kaynak}, {sure} sn)")


def mesaj_gelince(client, userdata, msg):
    global mod
    veri = json.loads(msg.payload)
    if veri.get("islem") == "mod":
        mod = veri["mod"]
        print("Mod:", mod)
    elif veri.get("islem") == "sula":
        sula(client, int(veri["saksi"]), float(veri["sure_sn"]), "manuel")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sulama-simulator")
    client.on_message = mesaj_gelince
    while True:
        try:
            client.connect(HOST, 1883)
            break
        except OSError:
            print("MQTT broker bekleniyor...")
            time.sleep(2)
    client.subscribe("sulama/komut")
    client.loop_start()

    while True:
        sicaklik = round(random.gauss(24, 1.5), 1)
        hava_nem = round(random.gauss(50, 5), 1)
        for sid, s in saksilar.items():
            # sıcaklık arttıkça daha hızlı kurur
            s["nem"] = max(5.0, s["nem"] - s["kuruma"] * (1 + (sicaklik - 24) * 0.05)
                           + random.uniform(-0.2, 0.2))
            if mod == "otomatik" and s["nem"] < 35:
                sula(client, sid, 8.0, "kural")
        client.publish("sulama/telemetri", json.dumps({
            "cihaz": "simulator",
            "sicaklik": sicaklik,
            "hava_nem": hava_nem,
            "saksilar": [{"saksi": sid, "toprak_nem": round(s["nem"], 1),
                          "ham": int(3000 - s["nem"] * 15), "vana": False}
                         for sid, s in saksilar.items()],
        }))
        time.sleep(ARALIK)


if __name__ == "__main__":
    main()
