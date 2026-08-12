from flask import Blueprint, jsonify, request, current_app, session

from extensions import db
from models import SearchLog, Airline
from providers.registry import get_active_providers

flights_bp = Blueprint("flights", __name__)


def _run_search(params):
    origin = (params.get("origin") or "").strip()
    destination = (params.get("destination") or "").strip()
    depart_date = params.get("depart_date") or params.get("departDate") or ""
    return_date = params.get("return_date") or params.get("returnDate") or None
    passengers = int(params.get("passengers") or 1)
    cabin_class = params.get("cabin_class") or params.get("cabinClass") or "economy"

    providers = get_active_providers(current_app.config.get("FLIGHT_PROVIDER", "mock"))
    all_flights = []
    for provider in providers:
        all_flights.extend(provider.search(
            origin=origin, destination=destination, depart_date=depart_date,
            return_date=return_date, passengers=passengers, cabin_class=cabin_class,
        ))
    return all_flights, {
        "origin": origin, "destination": destination, "depart_date": depart_date,
        "return_date": return_date, "passengers": passengers, "cabin_class": cabin_class,
    }


def _sort_flights(flights, sort_by):
    if sort_by == "price_desc":
        return sorted(flights, key=lambda f: f["price"], reverse=True)
    if sort_by == "fastest":
        return sorted(flights, key=lambda f: f["duration_minutes"])
    if sort_by == "fewest_stops":
        return sorted(flights, key=lambda f: (f["stops"], f["price"]))
    if sort_by == "best_value":
        # قيمة تقريبية: توازن بين السعر والمدة وعدد التوقفات (كلما قلّ الرقم كان أفضل)
        return sorted(flights, key=lambda f: f["price"] * 0.6 + f["duration_minutes"] * 0.3 + f["stops"] * 50)
    # الافتراضي: الأرخص إلى الأغلى
    return sorted(flights, key=lambda f: f["price"])


def _apply_filters(flights, args):
    price_min = args.get("price_min", type=float)
    price_max = args.get("price_max", type=float)
    max_stops = args.get("max_stops", type=int)
    airlines = args.getlist("airline") if hasattr(args, "getlist") else []
    departure_window = args.get("departure_window")  # morning/afternoon/evening/night

    result = flights
    if price_min is not None:
        result = [f for f in result if f["price"] >= price_min]
    if price_max is not None:
        result = [f for f in result if f["price"] <= price_max]
    if max_stops is not None:
        result = [f for f in result if f["stops"] <= max_stops]
    if airlines:
        result = [f for f in result if f["airline_code"] in airlines]
    if departure_window:
        def in_window(iso_time):
            hour = int(iso_time[11:13])
            if departure_window == "morning":
                return 5 <= hour < 12
            if departure_window == "afternoon":
                return 12 <= hour < 18
            if departure_window == "evening":
                return 18 <= hour < 24
            if departure_window == "night":
                return 0 <= hour < 5
            return True
        result = [f for f in result if in_window(f["depart_time"])]
    return result


@flights_bp.route("/api/flights/search", methods=["POST"])
def search_flights():
    payload = request.get_json(silent=True) or {}
    if not payload.get("origin") or not payload.get("destination") or not (payload.get("depart_date") or payload.get("departDate")):
        return jsonify({"error": "الرجاء تحديد نقطة الانطلاق والوجهة وتاريخ المغادرة"}), 400

    flights, meta = _run_search(payload)
    sort_by = payload.get("sort_by", "price_asc")
    flights = _sort_flights(flights, sort_by)

    # حفظ سجل البحث
    try:
        log = SearchLog(
            user_id=session.get("user_id"),
            origin=meta["origin"], destination=meta["destination"],
            depart_date=meta["depart_date"], return_date=meta["return_date"],
            passengers=meta["passengers"], cabin_class=meta["cabin_class"],
            results_count=len(flights),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

    airlines_available = sorted({(f["airline_code"], f["airline_name"], f["airline_name_ar"]) for f in flights})

    return jsonify({
        "meta": meta,
        "sort_by": sort_by,
        "count": len(flights),
        "flights": flights,
        "available_airlines": [
            {"code": c, "name": n, "name_ar": na} for c, n, na in airlines_available
        ],
        "is_mock_data": all(f.get("is_mock") for f in flights) if flights else True,
    })


@flights_bp.route("/api/flights/filter", methods=["POST"])
def filter_flights():
    """يعيد تنفيذ البحث نفسه ثم يطبق الفلاتر والترتيب - يُستخدم من صفحة النتائج."""
    payload = request.get_json(silent=True) or {}
    flights, meta = _run_search(payload)
    flights = _apply_filters(flights, request.args if not payload.get("filters") else _MultiDictShim(payload.get("filters", {})))
    sort_by = payload.get("sort_by", "price_asc")
    flights = _sort_flights(flights, sort_by)
    return jsonify({"meta": meta, "sort_by": sort_by, "count": len(flights), "flights": flights})


class _MultiDictShim:
    """يحاكي واجهة MultiDict البسيطة عندما تُرسل الفلاتر ضمن JSON بدل query string."""

    def __init__(self, d):
        self._d = d or {}

    def get(self, key, default=None, type=None):
        val = self._d.get(key, default)
        if val is not None and type is not None:
            try:
                return type(val)
            except (ValueError, TypeError):
                return default
        return val

    def getlist(self, key):
        val = self._d.get(key, [])
        return val if isinstance(val, list) else [val] if val else []


@flights_bp.route("/api/flights/details", methods=["POST"])
def flight_details():
    """
    نظرًا لأن بيانات Mock تُولَّد ديناميكيًا، نعيد تنفيذ نفس بحث الأصل/الوجهة/التاريخ
    ونبحث عن الرحلة صاحبة نفس المعرّف. مزود حقيقي مستقبلًا سيوفر endpoint مباشر لجلب رحلة بمعرفها.
    """
    payload = request.get_json(silent=True) or {}
    flight_id = payload.get("id")
    flights, meta = _run_search(payload)
    match = next((f for f in flights if f["id"] == flight_id), None)
    if not match:
        return jsonify({"error": "لم يتم العثور على الرحلة"}), 404
    return jsonify({"flight": match, "meta": meta})


@flights_bp.route("/api/flights/compare", methods=["POST"])
def compare_flights_route():
    from services.ai_service import AIService
    payload = request.get_json(silent=True) or {}
    flight_a = payload.get("flight_a")
    flight_b = payload.get("flight_b")
    if not flight_a or not flight_b:
        return jsonify({"error": "الرجاء إرسال بيانات الرحلتين للمقارنة"}), 400

    ai_service = AIService(current_app.config)
    comparison = ai_service.compare_flights(flight_a, flight_b)
    return jsonify(comparison)


@flights_bp.route("/api/airports", methods=["GET"])
def list_airports():
    """قائمة مطارات/مدن ثابتة لخانات الإكمال التلقائي في الصفحة الرئيسية."""
    from data.airports import AIRPORTS
    q = (request.args.get("q") or "").strip().lower()
    results = AIRPORTS
    if q:
        results = [
            a for a in AIRPORTS
            if q in a["city_ar"].lower() or q in a["city"].lower() or q in a["code"].lower()
        ]
    return jsonify(results[:20])
