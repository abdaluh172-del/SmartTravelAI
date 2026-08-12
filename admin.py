from flask import Blueprint, jsonify, session, current_app

from models import User, Airline, SearchLog, TripPlan, Destination
from providers.registry import PROVIDERS

admin_bp = Blueprint("admin", __name__)


def _require_admin():
    user_id = session.get("user_id")
    if not user_id:
        return False
    user = User.query.get(user_id)
    return bool(user and user.is_admin)


@admin_bp.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not _require_admin():
        return jsonify({"error": "غير مصرح لك بالوصول"}), 403

    return jsonify({
        "users_count": User.query.count(),
        "airlines_count": Airline.query.count(),
        "destinations_count": Destination.query.count(),
        "searches_count": SearchLog.query.count(),
        "trip_plans_count": TripPlan.query.count(),
    })


@admin_bp.route("/api/admin/searches", methods=["GET"])
def admin_searches():
    if not _require_admin():
        return jsonify({"error": "غير مصرح لك بالوصول"}), 403
    logs = SearchLog.query.order_by(SearchLog.created_at.desc()).limit(100).all()
    return jsonify([l.to_dict() for l in logs])


@admin_bp.route("/api/admin/airlines", methods=["GET"])
def admin_airlines():
    if not _require_admin():
        return jsonify({"error": "غير مصرح لك بالوصول"}), 403
    airlines = Airline.query.all()
    return jsonify([a.to_dict() for a in airlines])


@admin_bp.route("/api/admin/users", methods=["GET"])
def admin_users():
    if not _require_admin():
        return jsonify({"error": "غير مصرح لك بالوصول"}), 403
    users = User.query.order_by(User.created_at.desc()).limit(200).all()
    return jsonify([u.to_dict() for u in users])


@admin_bp.route("/api/admin/providers-status", methods=["GET"])
def admin_providers_status():
    if not _require_admin():
        return jsonify({"error": "غير مصرح لك بالوصول"}), 403
    return jsonify({
        "flight_providers": [{"key": k, "is_mock": v.is_mock} for k, v in PROVIDERS.items()],
        "active_flight_provider": current_app.config.get("FLIGHT_PROVIDER", "mock"),
        "ai_provider": current_app.config.get("AI_PROVIDER", "mock"),
        "ai_key_configured": bool(current_app.config.get("ANTHROPIC_API_KEY")),
    })
