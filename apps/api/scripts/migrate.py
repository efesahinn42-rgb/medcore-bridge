"""infra/supabase/migrations/*.sql dosyalarını sırayla, uygulanmamış olanları çalıştırır."""

import asyncio
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

MIGRATIONS_DIR = (
    Path(__file__).resolve().parents[3] / "infra" / "supabase" / "migrations"
)


async def main() -> None:
    load_dotenv()
    conn = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=15)
    await conn.execute(
        """
        create table if not exists schema_migrations (
          filename text primary key,
          applied_at timestamptz not null default now()
        )
        """
    )
    applied = {
        r["filename"]
        for r in await conn.fetch("select filename from schema_migrations")
    }

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        print(f"Applying {path.name} ...")
        sql = path.read_text()
        async with conn.transaction():
            await conn.execute(sql)
            await conn.execute(
                "insert into schema_migrations (filename) values ($1)", path.name
            )
        print("  OK")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
