import json

from flask import Blueprint, jsonify, request, current_app, session

from extensions import db
from models import TripPlan
from services.ai_service import AIService

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/popular-places", methods=["POST"])
def popular_places():
    payload = request.get_json(silent=True) or {}
    destination = payload.get("destination")
    if not destination:
        return jsonify({"error": "الرجاء تحديد الوجهة"}), 400

    ai_service = AIService(current_app.config)
    places = ai_service.get_popular_places(destination)
    return jsonify({"destination": destination, "places": places, "is_mock": ai_service.is_mock})


@ai_bp.route("/api/ai/plan-trip", methods=["POST"])
def plan_trip():
    """مساعد السفر الذكي -> 'خطط لي رحلتي' (نموذج بمدخلات محددة)."""
    payload = request.get_json(silent=True) or {}
    destination = payload.get("destination")
    days = payload.get("days", 3)
    budget = payload.get("budget", 0)
    trip_type = payload.get("trip_type", "فردية")
    interests = payload.get("interests", "")

    if not destination:
        return jsonify({"error": "الرجاء تحديد الوجهة"}), 400

    ai_service = AIService(current_app.config)
    itinerary = ai_service.generate_itinerary(destination, days, budget, trip_type, interests)

    _save_trip_plan(destination, days, budget, trip_type, interests, itinerary)
    return jsonify(itinerary)


@ai_bp.route("/api/ai/plan-full-trip", methods=["POST"])
def plan_full_trip():
    """زر 'خطط رحلتي بالكامل' - يقبل نصًا حرًا مثل: أبي أسافر 5 أيام وميزانيتي 5000 ريال..."""
    payload = request.get_json(silent=True) or {}
    prompt_text = (payload.get("prompt") or "").strip()
    if not prompt_text:
        return jsonify({"error": "الرجاء كتابة تفاصيل رحلتك"}), 400

    context = {
        "destination": payload.get("destination") or _extract_hint(prompt_text, "destination"),
        "days": payload.get("days") or _extract_days(prompt_text),
        "budget": payload.get("budget") or _extract_budget(prompt_text),
        "trip_type": payload.get("trip_type") or "فردية",
        "interests": payload.get("interests") or prompt_text,
    }

    ai_service = AIService(current_app.config)
    full_plan = ai_service.free_text_plan(prompt_text, context)

    _save_trip_plan(
        context["destination"] or "غير محدد", context["days"], context["budget"],
        context["trip_type"], context["interests"], full_plan,
    )
    return jsonify(full_plan)


def _extract_days(text):
    import re
    m = re.search(r"(\d+)\s*(يوم|أيام)", text)
    return int(m.group(1)) if m else 5


def _extract_budget(text):
    import re
    m = re.search(r"(\d{3,6})\s*(ريال|SAR|درهم|دولار)?", text)
    return float(m.group(1)) if m else 5000.0


def _extract_hint(text, field):
    # تبسيط: بدون مزود NLP حقيقي، نترك الوجهة فارغة إن لم تُذكر صراحة عبر الحقول المنظمة
    return None


def _save_trip_plan(destination, days, budget, trip_type, interests, plan):
    try:
        record = TripPlan(
            user_id=session.get("user_id"),
            destination=destination,
            days=plan.get("days", days),
            budget=budget,
            trip_type=trip_type,
            interests=interests if isinstance(interests, str) else json.dumps(interests, ensure_ascii=False),
            plan_json=json.dumps(plan, ensure_ascii=False),
            is_mock=plan.get("is_mock", True),
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
