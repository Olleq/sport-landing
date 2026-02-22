from flask import Blueprint, jsonify
from .db import get_db

public_bp = Blueprint("public", __name__)

@public_bp.get("/health")
def health():
    return jsonify({"ok": True})

@public_bp.get("/debug/default-campaign")
def debug_default_campaign():
    db = get_db()
    row = db.execute(
        "SELECT id, name, is_active, is_default, mode, primary_code FROM campaigns WHERE is_default=1 LIMIT 1"
    ).fetchone()
    return jsonify({"default_campaign": dict(row) if row else None})
