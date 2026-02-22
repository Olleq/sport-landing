import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DB_PATH = os.environ.get("DB_PATH", "database.db")  # SQLite file in working dir
