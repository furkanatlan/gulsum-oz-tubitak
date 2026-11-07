"""Sulama olayları ve web arayüzünden gönderilen komutlar."""
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config, mqtt_client
from ..db import get_db
from ..models import SulamaOlayi

router = APIRouter(prefix="/api/sulama", tags=["sulama"])


class ManuelSulama(BaseModel):
    saksi_id: int = Field(ge=1, le=3)
    sure_sn: float = Field(gt=0, le=120)  # güvenlik için en fazla 2 dakika


class ModDegistir(BaseModel):
    mod: Literal["otomatik", "manuel"]


@router.get("/olaylar")
def olaylar(saksi_id: int | None = None, limit: int = 100, db: Session = Depends(get_db)):
    sorgu = select(SulamaOlayi).order_by(SulamaOlayi.zaman.desc()).limit(limit)
    if saksi_id is not None:
        sorgu = sorgu.where(SulamaOlayi.saksi_id == saksi_id)
    return db.scalars(sorgu).all()


@router.post("/manuel")
def manuel_sula(istek: ManuelSulama):
    mqtt_client.yayinla(config.KONU_KOMUT, {"islem": "sula", "saksi": istek.saksi_id,
                                            "sure_sn": istek.sure_sn})
    return {"durum": "komut gönderildi"}


@router.post("/mod")
def mod_degistir(istek: ModDegistir):
    # retain=True: ESP32 yeniden başlarsa son modu broker'dan geri alır
    mqtt_client.yayinla(config.KONU_KOMUT, {"islem": "mod", "mod": istek.mod}, retain=True)
    return {"durum": "komut gönderildi", "mod": istek.mod}
