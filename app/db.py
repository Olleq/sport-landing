import sqlite3
from pathlib import Path
from flask import g
from .config import Config

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(Config.DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(Config.DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON;")
    schema_path = Path(__file__).with_name("models.sql")
    db.executescript(schema_path.read_text(encoding="utf-8"))
    db.commit()
    db.close()

def seed_default_campaign():
    db = sqlite3.connect(Config.DB_PATH)
    db.row_factory = sqlite3.Row

    row = db.execute(
        "SELECT id FROM campaigns WHERE is_default=1 LIMIT 1"
    ).fetchone()

    if not row:
        db.execute(
            "INSERT INTO campaigns (name, is_active, is_default, mode, primary_code) VALUES (?, ?, ?, ?, ?)",
            ("SPORT_DEFAULT", 1, 1, "fixed", "SPORT10"),
        )
        db.commit()

    db.close()
