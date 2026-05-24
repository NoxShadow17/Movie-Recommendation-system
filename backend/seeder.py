"""
Auto-seeder: loads seed_data/seed_data.json.gz into the database
if the database is empty. Runs once on startup.
"""
import gzip
import json
import os
import logging
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal

logger = logging.getLogger(__name__)

SEED_FILE = os.path.join(os.path.dirname(__file__), 'seed_data', 'seed_data.json.gz')

# Tables and their insert order (respecting foreign key dependencies)
# Note: user_friends is excluded — it's not in the SQLAlchemy schema (friendships covers it)
TABLE_ORDER = [
    'users',
    'movies',
    'ratings',
    'friendships',
    'user_watchlist',
    'trending_movies',
]


def _db_is_empty(db: Session) -> bool:
    """Check if the database has any users yet."""
    try:
        result = db.execute(__import__('sqlalchemy').text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        return count == 0
    except Exception:
        return True


def _bulk_insert(db: Session, table: str, rows: list):
    """Insert rows into a table using raw SQL for speed."""
    if not rows:
        return
    from sqlalchemy import text

    columns = list(rows[0].keys())
    col_str = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join(f":{c}" for c in columns)
    stmt = text(f'INSERT OR IGNORE INTO "{table}" ({col_str}) VALUES ({placeholders})')

    BATCH = 500
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        db.execute(stmt, batch)
    db.commit()


def run_seed():
    """Seed the database from the compressed JSON file if it's empty."""
    if not os.path.exists(SEED_FILE):
        logger.warning(f"Seed file not found at {SEED_FILE}, skipping seeding.")
        return

    db: Session = SessionLocal()
    try:
        if not _db_is_empty(db):
            logger.info("Database already has data — skipping seed.")
            return

        logger.info("Database is empty. Loading seed data...")
        with gzip.open(SEED_FILE, 'rt', encoding='utf-8') as f:
            data = json.load(f)

        for table in TABLE_ORDER:
            rows = data.get(table, [])
            if not rows:
                continue
            try:
                logger.info(f"  Seeding {len(rows)} rows into '{table}'...")
                _bulk_insert(db, table, rows)
                logger.info(f"  ✓ '{table}' done.")
            except Exception as e:
                logger.warning(f"  ⚠ Skipping '{table}': {e}")
                db.rollback()  # rollback only this table's failed transaction

        logger.info("✅ Seed complete! Database is ready.")
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()
