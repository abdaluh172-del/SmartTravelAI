from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "travel-ai-backend",
        "ai_provider": current_app.config.get("AI_PROVIDER", "mock"),
        "flight_provider": current_app.config.get("FLIGHT_PROVIDER", "mock"),
    })
