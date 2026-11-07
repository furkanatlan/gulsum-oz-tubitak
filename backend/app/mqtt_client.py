"""MQTT köprüsü: ESP32'den gelen mesajları veritabanına yazar, komutları ESP32'ye gönderir.

Mesaj biçimleri (JSON) için bkz. PROJE_PLANI.md -> "MQTT mesaj sözleşmesi".
"""
import json
import logging

import paho.mqtt.client as mqtt

from . import config
from .db import SessionLocal
from .models import Olcum, SulamaOlayi

log = logging.getLogger("mqtt")
_istemci: mqtt.Client | None = None


def _telemetri_kaydet(veri: dict) -> None:
    with SessionLocal() as db:
        for s in veri.get("saksilar", []):
            db.add(Olcum(
                saksi_id=s["saksi"],
                toprak_nem=s["toprak_nem"],
                toprak_ham=s.get("ham"),
                sicaklik=veri.get("sicaklik"),
                hava_nem=veri.get("hava_nem"),
                vana_acik=bool(s.get("vana", False)),
            ))
        db.commit()


def _olay_kaydet(veri: dict) -> None:
    sure = float(veri["sure_sn"])
    su_ml = veri.get("su_ml")
    if su_ml is None:  # ESP32 su miktarını göndermediyse pompa debisinden hesapla
        su_ml = sure / 60 * config.POMPA_DEBI_ML_DK
    with SessionLocal() as db:
        db.add(SulamaOlayi(saksi_id=veri["saksi"], sure_sn=sure, su_ml=su_ml,
                           kaynak=veri.get("kaynak", "bilinmiyor")))
        db.commit()


def _baglaninca(client, userdata, flags, reason_code, properties):
    log.info("MQTT broker'a bağlanıldı (%s)", reason_code)
    client.subscribe(config.KONU_TELEMETRI)
    client.subscribe(config.KONU_OLAY)


def _mesaj_gelince(client, userdata, msg):
    try:
        veri = json.loads(msg.payload)
        if msg.topic == config.KONU_TELEMETRI:
            _telemetri_kaydet(veri)
        elif msg.topic == config.KONU_OLAY:
            _olay_kaydet(veri)
    except Exception:  # hatalı bir mesaj tüm sistemi durdurmasın
        log.exception("Mesaj işlenemedi: %s %s", msg.topic, msg.payload[:200])


def baslat() -> None:
    global _istemci
    _istemci = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sulama-backend")
    _istemci.on_connect = _baglaninca
    _istemci.on_message = _mesaj_gelince
    _istemci.connect_async(config.MQTT_HOST, config.MQTT_PORT)
    _istemci.loop_start()  # arka planda çalışır, bağlantı koparsa yeniden bağlanır


def durdur() -> None:
    if _istemci:
        _istemci.loop_stop()
        _istemci.disconnect()


def yayinla(konu: str, veri: dict, retain: bool = False) -> None:
    if _istemci is None:
        raise RuntimeError("MQTT istemcisi başlatılmadı")
    _istemci.publish(konu, json.dumps(veri), qos=1, retain=retain)
