from flask import Blueprint, jsonify, request
from datetime import datetime
import re
import secrets

from .db import get_db

public_bp = Blueprint("public", __name__)

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


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


@public_bp.post("/api/signup")
def signup():
    data = request.get_json()

    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"].strip().lower()

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Invalid email"}), 400

    db = get_db()

    # kampania z parametru lub default
    camp_param = request.args.get("camp")

    if camp_param:
        campaign = db.execute(
            "SELECT * FROM campaigns WHERE name=? AND is_active=1 LIMIT 1",
            (camp_param,),
        ).fetchone()
    else:
        campaign = db.execute(
            "SELECT * FROM campaigns WHERE is_default=1 AND is_active=1 LIMIT 1"
        ).fetchone()

    if not campaign:
        return jsonify({"error": "No active campaign"}), 400

    token = secrets.token_urlsafe(32)
    now = datetime.utcnow().isoformat()

    try:
        db.execute(
            """
            INSERT INTO signups (camp_id, channel, email, status, token, created_at)
            VALUES (?, ?, ?, 'pending', ?, ?)
            """,
            (campaign["id"], request.args.get("ch"), email, token, now),
        )
        db.commit()
    except Exception:
        return jsonify({"error": "Email already registered in this campaign"}), 400

    return jsonify({
        "message": "Signup created",
        "token": token  # tymczasowo zwracamy do testów
    })
