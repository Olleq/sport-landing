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
