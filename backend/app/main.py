"""Akıllı Sulama Sistemi - Backend (FastAPI)

API belgeleri (otomatik): http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from . import config, mqtt_client
from .db import Base, SessionLocal, engine
from .models import Saksi
from .routers import disa_aktar, goruntuler, olcumler, saksilar, sulama

logging.basicConfig(level=logging.INFO)


def _baslangic_verisi() -> None:
    """Tablolar yoksa oluşturur ve 3 deney saksısını ekler."""
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Saksi).limit(1)) is None:
            for sid, tur in config.SAKSILAR.items():
                db.add(Saksi(id=sid, ad=f"Saksı {sid} ({tur})", toprak_turu=tur))
            db.commit()


@asynccontextmanager
async def yasam_dongusu(app: FastAPI):
    _baslangic_verisi()
    mqtt_client.baslat()
    yield
    mqtt_client.durdur()


app = FastAPI(title="Akıllı Sulama Sistemi API", lifespan=yasam_dongusu)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

for r in (saksilar, olcumler, sulama, goruntuler, disa_aktar):
    app.include_router(r.router)


@app.get("/api/saglik", tags=["sistem"])
def saglik():
    return {"durum": "çalışıyor"}
