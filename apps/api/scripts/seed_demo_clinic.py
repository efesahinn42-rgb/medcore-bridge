"""Demo/geliştirme için tek bir klinik oluşturur (yoksa) ve örnek bir SSS dokümanı embed eder.
Klinik zaten varsa (slug ile) sadece FAQ'ı yeniden ingest eder (idempotent).

Kullanım: uv run python scripts/seed_demo_clinic.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncpg
from dotenv import load_dotenv

from app.services.rag import ingest_document

SLUG = "demo-klinik"

FAQ_DOCUMENT = """Saç ekimi fiyatlarımız greft sayısına göre 1500 dolardan başlamaktadır.
FUE tekniği ile 4000 grefte kadar tek seansta işlem yapılabilir.

Diş implant fiyatlarımız 400 dolardan başlamaktadır, materyal ve marka seçimine göre değişir.
Gülüş tasarımı paketleri 2000 dolardan başlamaktadır.

Kliniğimiz hafta içi 09:00-18:00, cumartesi 10:00-14:00 arası hizmet vermektedir. Pazar
günleri kapalıyız.

Yurt dışından gelen hastalarımız için havalimanı transferi ve otel konaklaması paket
fiyatına dahildir. Konaklama süresi işlem tipine göre 3-7 gün arasında değişir.

Saç ekimi sonrası ilk yıkama işlemi klinikte uzman ekibimiz tarafından yapılır. İyileşme
süreci ortalama 10-14 gün sürer, kesin sonuç 12 ay içinde ortaya çıkar."""


async def main() -> None:
    load_dotenv()
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])

    clinic_id = await conn.fetchval("select id from clinics where slug = $1", SLUG)
    if clinic_id is None:
        clinic_id = await conn.fetchval(
            "insert into clinics (name, slug, supported_languages) "
            "values ('Demo Klinik', $1, array['tr','en']) returning id",
            SLUG,
        )
        print(f"Klinik oluşturuldu: {clinic_id}")
    else:
        print(f"Klinik zaten var: {clinic_id}")

    await conn.close()

    chunk_count = await ingest_document(clinic_id, "demo_faq.txt", FAQ_DOCUMENT)
    print(f"FAQ ingest edildi: {chunk_count} chunk")
    print(f"\nCLINIC_ID={clinic_id}")


if __name__ == "__main__":
    asyncio.run(main())
