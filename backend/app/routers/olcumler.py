"""Sensör ölçümleri (grafikler için)."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Olcum

router = APIRouter(prefix="/api/olcumler", tags=["ölçümler"])


@router.get("")
def olcumler(saksi_id: int | None = None, saat: int = Query(24, ge=1, le=24 * 60),
             db: Session = Depends(get_db)):
    """Son `saat` saatteki ölçümler, eskiden yeniye sıralı."""
    baslangic = datetime.now(timezone.utc) - timedelta(hours=saat)
    sorgu = select(Olcum).where(Olcum.zaman >= baslangic).order_by(Olcum.zaman)
    if saksi_id is not None:
        sorgu = sorgu.where(Olcum.saksi_id == saksi_id)
    return db.scalars(sorgu).all()
