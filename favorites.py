import json

from flask import Blueprint, jsonify, request, session

from extensions import db
from models import Favorite

favorites_bp = Blueprint("favorites", __name__)


def _require_login():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


@favorites_bp.route("/api/favorites", methods=["GET"])
def list_favorites():
    user_id = _require_login()
    if not user_id:
        return jsonify({"error": "يجب تسجيل الدخول"}), 401
    items = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()
    return jsonify([f.to_dict() for f in items])


@favorites_bp.route("/api/favorites", methods=["POST"])
def add_favorite():
    user_id = _require_login()
    if not user_id:
        return jsonify({"error": "يجب تسجيل الدخول"}), 401

    payload = request.get_json(silent=True) or {}
    item_type = payload.get("item_type")
    item_ref = payload.get("item_ref")
    item_data = payload.get("item_data")

    if not item_type or not item_ref:
        return jsonify({"error": "بيانات غير مكتملة"}), 400

    fav = Favorite(
        user_id=user_id, item_type=item_type, item_ref=str(item_ref),
        item_data=json.dumps(item_data, ensure_ascii=False) if item_data else None,
    )
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.to_dict()), 201


@favorites_bp.route("/api/favorites/<int:fav_id>", methods=["DELETE"])
def remove_favorite(fav_id):
    user_id = _require_login()
    if not user_id:
        return jsonify({"error": "يجب تسجيل الدخول"}), 401

    fav = Favorite.query.filter_by(id=fav_id, user_id=user_id).first()
    if not fav:
        return jsonify({"error": "غير موجود"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "تم الحذف"})
