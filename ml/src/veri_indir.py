"""Backend'den deney verisini indirir -> data/veri.csv

Çalıştırma:  docker compose exec ml python src/veri_indir.py
"""
import os
from pathlib import Path

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
HEDEF = Path(__file__).resolve().parent.parent / "data" / "veri.csv"

yanit = requests.get(f"{API_URL}/api/disa-aktar/veri.csv", timeout=60)
yanit.raise_for_status()
HEDEF.write_bytes(yanit.content)
print(f"{HEDEF} kaydedildi ({len(yanit.content.splitlines()) - 1} satır)")
