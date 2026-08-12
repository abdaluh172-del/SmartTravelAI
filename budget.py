from flask import Blueprint, jsonify, request

from services.budget_service import estimate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/api/budget/estimate", methods=["POST"])
def budget_estimate():
    payload = request.get_json(silent=True) or {}
    flight_price_total = float(payload.get("flight_price_total", 0) or 0)
    days = int(payload.get("days", 1) or 1)
    tier = payload.get("tier", "mid")
    passengers = int(payload.get("passengers", 1) or 1)

    result = estimate_budget(flight_price_total, days, tier, passengers)
    return jsonify(result)
