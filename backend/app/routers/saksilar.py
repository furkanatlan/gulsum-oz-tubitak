"""Saksı listesi ve gösterge paneli özeti."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Goruntu, Olcum, Saksi, SulamaOlayi

router = APIRouter(prefix="/api/saksilar", tags=["saksılar"])


@router.get("")
def saksi_listesi(db: Session = Depends(get_db)):
    return db.scalars(select(Saksi).order_by(Saksi.id)).all()


@router.get("/ozet")
def ozet(db: Session = Depends(get_db)):
    """Her saksı için son ölçüm, son fotoğraf ve su tüketimi (web arayüzünün ana ekranı)."""
    gun_basi = datetime.now(timezone.utc) - timedelta(hours=24)
    sonuc = []
    for saksi in db.scalars(select(Saksi).order_by(Saksi.id)):
        son_olcum = db.scalars(select(Olcum).where(Olcum.saksi_id == saksi.id)
                               .order_by(Olcum.zaman.desc()).limit(1)).first()
        son_goruntu = db.scalars(select(Goruntu).where(Goruntu.saksi_id == saksi.id)
                                 .order_by(Goruntu.zaman.desc()).limit(1)).first()
        toplam_su = db.scalar(select(func.coalesce(func.sum(SulamaOlayi.su_ml), 0))
                              .where(SulamaOlayi.saksi_id == saksi.id))
        su_24s = db.scalar(select(func.coalesce(func.sum(SulamaOlayi.su_ml), 0))
                           .where(SulamaOlayi.saksi_id == saksi.id, SulamaOlayi.zaman >= gun_basi))
        sonuc.append({
            "saksi": saksi,
            "son_olcum": son_olcum,
            "son_goruntu": son_goruntu,
            "toplam_su_ml": toplam_su,
            "son_24_saat_su_ml": su_24s,
        })
    return sonuc
