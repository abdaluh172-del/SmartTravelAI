from flask import Blueprint, jsonify, request, session

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not full_name or not email or len(password) < 6:
        return jsonify({"error": "الرجاء إدخال الاسم والبريد الإلكتروني وكلمة مرور لا تقل عن 6 أحرف"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "هذا البريد الإلكتروني مسجل مسبقًا"}), 409

    user = User(full_name=full_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}), 401

    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "تم تسجيل الخروج"})


@auth_bp.route("/api/auth/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None})
    user = User.query.get(user_id)
    return jsonify({"user": user.to_dict() if user else None})
