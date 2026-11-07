"""Veritabanı tabloları."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def simdi() -> datetime:
    return datetime.now(timezone.utc)


class Saksi(Base):
    __tablename__ = "saksilar"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ad: Mapped[str] = mapped_column(String(50))
    toprak_turu: Mapped[str] = mapped_column(String(20))  # kumlu / killi / tinli


class Olcum(Base):
    """ESP32'den gelen her sensör ölçümü (saksı başına bir satır)."""
    __tablename__ = "olcumler"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zaman: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=simdi, index=True)
    saksi_id: Mapped[int] = mapped_column(ForeignKey("saksilar.id"), index=True)
    toprak_nem: Mapped[float] = mapped_column(Float)            # %
    toprak_ham: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ADC ham değeri
    sicaklik: Mapped[float | None] = mapped_column(Float, nullable=True)    # °C
    hava_nem: Mapped[float | None] = mapped_column(Float, nullable=True)    # %
    vana_acik: Mapped[bool] = mapped_column(Boolean, default=False)


class SulamaOlayi(Base):
    __tablename__ = "sulama_olaylari"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zaman: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=simdi, index=True)
    saksi_id: Mapped[int] = mapped_column(ForeignKey("saksilar.id"), index=True)
    sure_sn: Mapped[float] = mapped_column(Float)
    su_ml: Mapped[float] = mapped_column(Float)
    kaynak: Mapped[str] = mapped_column(String(20))  # model / kural / manuel


class Goruntu(Base):
    __tablename__ = "goruntuler"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zaman: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=simdi, index=True)
    saksi_id: Mapped[int] = mapped_column(ForeignKey("saksilar.id"), index=True)
    dosya: Mapped[str] = mapped_column(String(255))
    yesil_oran: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-1 arası
