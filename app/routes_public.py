from flask import Blueprint, jsonify, request
from datetime import datetime
import re
import secrets
import smtplib
from email.message import EmailMessage
from .config import Config

from .db import get_db, init_db

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
    init_db()
    seed_default_campaign()
    
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
        send_confirmation_email(email, token)
    except Exception:
        return jsonify({"error": "Email already registered in this campaign"}), 400

    return jsonify({
        "message": "Signup created",
        "token": token  # tymczasowo zwracamy do testów
    })

def send_confirmation_email(to_email, token):
    if not Config.SMTP_HOST:
        print("SMTP not configured, skipping email")
        return

    msg = EmailMessage()
    msg["Subject"] = "Potwierdź zapis – Zdrowie Na Stole"
    msg["From"] = Config.SMTP_FROM
    msg["To"] = to_email

    confirm_url = f"https://sport-landing.onrender.com/confirm?token={token}"

    msg.set_content(f"""
Dziękujemy za zapis!

Kliknij poniższy link, aby potwierdzić:
{confirm_url}
""")

    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
        server.starttls()
        server.login(Config.SMTP_USER, Config.SMTP_PASS)
        server.send_message(msg)

@public_bp.get("/confirm")
def confirm():
    token = request.args.get("token")

    if not token:
        return jsonify({"error": "Token is required"}), 400

    db = get_db()

    signup = db.execute(
        "SELECT * FROM signups WHERE token=? LIMIT 1",
        (token,),
    ).fetchone()

    if not signup:
        return jsonify({"error": "Invalid token"}), 400

    if signup["status"] == "confirmed":
        return jsonify({"message": "Already confirmed", "code": signup["assigned_code"]})

    campaign = db.execute(
        "SELECT * FROM campaigns WHERE id=?",
        (signup["camp_id"],),
    ).fetchone()

    if not campaign:
        return jsonify({"error": "Campaign not found"}), 400

    # TRYB STAŁY (fixed)
    if campaign["mode"] == "fixed":
        assigned_code = campaign["primary_code"]

    else:
        # tryb indywidualny – pierwszy wolny kod
        code_row = db.execute(
            "SELECT * FROM codes WHERE camp_id=? AND is_used=0 LIMIT 1",
            (campaign["id"],),
        ).fetchone()

        if not code_row:
            return jsonify({"error": "No codes available"}), 400

        assigned_code = code_row["code"]

        db.execute(
            "UPDATE codes SET is_used=1, used_by_signup_id=?, used_at=datetime('now') WHERE id=?",
            (signup["id"], code_row["id"]),
        )

    db.execute(
        "UPDATE signups SET status='confirmed', assigned_code=?, confirmed_at=datetime('now') WHERE id=?",
        (assigned_code, signup["id"]),
    )

    db.commit()

    return jsonify({
        "message": "Confirmed",
        "code": assigned_code
    })
