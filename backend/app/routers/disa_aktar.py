"""Makine öğrenmesi için veri dışa aktarma (CSV).

Her ölçüm satırına şu bilgiler eklenir:
  - saksının toprak türü
  - o ana kadarki en son yeşil oran (fotoğraftan)
  - son sulamadan bu yana geçen dakika
  - o ölçümden sonraki ilk sulamada verilen su (etiket üretmek için)
"""
import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Goruntu, Olcum, Saksi, SulamaOlayi

router = APIRouter(prefix="/api/disa-aktar", tags=["dışa aktarma"])

SUTUNLAR = ["zaman", "saksi_id", "toprak_turu", "toprak_nem", "sicaklik", "hava_nem",
            "vana_acik", "yesil_oran", "son_sulamadan_dk", "sonraki_sulama_dk", "sonraki_sulama_ml"]


@router.get("/veri.csv")
def veri_csv(db: Session = Depends(get_db)):
    turler = {s.id: s.toprak_turu for s in db.scalars(select(Saksi))}
    tampon = io.StringIO()
    yazici = csv.writer(tampon)
    yazici.writerow(SUTUNLAR)

    for saksi_id, tur in turler.items():
        olcumler = db.scalars(select(Olcum).where(Olcum.saksi_id == saksi_id).order_by(Olcum.zaman)).all()
        olaylar = db.scalars(select(SulamaOlayi).where(SulamaOlayi.saksi_id == saksi_id)
                             .order_by(SulamaOlayi.zaman)).all()
        goruntuler = db.scalars(select(Goruntu).where(Goruntu.saksi_id == saksi_id)
                                .order_by(Goruntu.zaman)).all()
        i_olay = i_gor = 0
        son_olay = son_gor = None
        for o in olcumler:
            while i_olay < len(olaylar) and olaylar[i_olay].zaman <= o.zaman:
                son_olay = olaylar[i_olay]
                i_olay += 1
            while i_gor < len(goruntuler) and goruntuler[i_gor].zaman <= o.zaman:
                son_gor = goruntuler[i_gor]
                i_gor += 1
            sonraki = olaylar[i_olay] if i_olay < len(olaylar) else None
            yazici.writerow([
                o.zaman.isoformat(), saksi_id, tur, o.toprak_nem, o.sicaklik, o.hava_nem,
                int(o.vana_acik),
                son_gor.yesil_oran if son_gor else "",
                round((o.zaman - son_olay.zaman).total_seconds() / 60, 1) if son_olay else "",
                round((sonraki.zaman - o.zaman).total_seconds() / 60, 1) if sonraki else "",
                sonraki.su_ml if sonraki else "",
            ])

    tampon.seek(0)
    return StreamingResponse(iter([tampon.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=veri.csv"})
