from flask import Flask
from .config import Config
from .db import init_db, close_db, seed_default_campaign
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


app = create_app()
