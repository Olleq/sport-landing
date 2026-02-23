from flask import Flask
from .config import Config
from .db import init_db, get_db, close_db
from .routes_public import public_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # DB lifecycle
    app.teardown_appcontext(close_db)

        # 🔴 INIT DB PRZY STARCIE
    with app.app_context():
        init_db()
        seed_default_campaign()

    # Routes
    app.register_blueprint(public_bp)

    @app.get("/")
    def home():
        return "Strefa Sport Zdrowie-Na-Stole działa"

    return app

def seed_default_campaign():
    db = get_db()
    # jeśli nie ma żadnej domyślnej kampanii, tworzymy
    row = db.execute("SELECT id FROM campaigns WHERE is_default=1 LIMIT 1").fetchone()
    if row:
        return

    db.execute(
        "INSERT INTO campaigns (name, is_active, is_default, mode, primary_code) VALUES (?, ?, ?, ?, ?)",
        ("SPORT_DEFAULT", 1, 1, "fixed", "SPORT10"),
    )
    db.commit()

app = create_app()
