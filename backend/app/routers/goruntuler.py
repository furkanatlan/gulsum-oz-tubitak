"""ESP32-CAM fotoğraf yükleme ve görüntüleme.

ESP32-CAM, fotoğrafı ham JPEG olarak gönderir:
    POST /api/goruntuler/yukle?saksi_id=1   (Content-Type: image/jpeg)
"""
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config, mqtt_client
from ..db import get_db
from ..goruntu_analiz import yesil_oran_hesapla
from ..models import Goruntu

router = APIRouter(prefix="/api/goruntuler", tags=["görüntüler"])
AZAMI_BOYUT = 2 * 1024 * 1024  # 2 MB


@router.post("/yukle")
async def yukle(saksi_id: int, request: Request, db: Session = Depends(get_db)):
    icerik = await request.body()
    if not icerik or len(icerik) > AZAMI_BOYUT:
        raise HTTPException(400, "Boş ya da çok büyük dosya")
    if not icerik.startswith(b"\xff\xd8"):
        raise HTTPException(400, "Dosya JPEG değil")

    os.makedirs(config.IMAGE_DIR, exist_ok=True)
    ad = f"saksi{saksi_id}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.jpg"
    yol = os.path.join(config.IMAGE_DIR, ad)
    with open(yol, "wb") as f:
        f.write(icerik)

    oran = yesil_oran_hesapla(yol)
    kayit = Goruntu(saksi_id=saksi_id, dosya=ad, yesil_oran=oran)
    db.add(kayit)
    db.commit()

    # Modelin kullanabilmesi için yeşil oranı ESP32'ye bildir
    mqtt_client.yayinla(config.KONU_BITKI_INDEKSI, {"saksi": saksi_id, "yesil_oran": oran},
                        retain=True)
    return {"id": kayit.id, "yesil_oran": oran}


@router.get("")
def liste(saksi_id: int | None = None, limit: int = 20, db: Session = Depends(get_db)):
    sorgu = select(Goruntu).order_by(Goruntu.zaman.desc()).limit(limit)
    if saksi_id is not None:
        sorgu = sorgu.where(Goruntu.saksi_id == saksi_id)
    return db.scalars(sorgu).all()


@router.get("/{goruntu_id}/dosya")
def dosya(goruntu_id: int, db: Session = Depends(get_db)):
    kayit = db.get(Goruntu, goruntu_id)
    if kayit is None:
        raise HTTPException(404, "Görüntü bulunamadı")
    return FileResponse(os.path.join(config.IMAGE_DIR, kayit.dosya), media_type="image/jpeg")
