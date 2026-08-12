"""
Budget Service
==============
حساب تقديري لتكلفة الرحلة الإجمالية. مستقل عن مزودي الفنادق/الأنشطة
الحقيقيين حتى يتم ربطهم لاحقًا - حاليًا يعتمد على متوسطات تقديرية.
"""

DAILY_HOTEL_ESTIMATE = {"economy": 250, "mid": 450, "luxury": 900}
DAILY_FOOD_ESTIMATE = {"economy": 120, "mid": 220, "luxury": 450}
DAILY_TRANSPORT_ESTIMATE = {"economy": 60, "mid": 120, "luxury": 300}
DAILY_ACTIVITIES_ESTIMATE = {"economy": 80, "mid": 180, "luxury": 400}


def estimate_budget(flight_price_total, days, tier="mid", passengers=1):
    days = max(1, int(days or 1))
    tier = tier if tier in DAILY_HOTEL_ESTIMATE else "mid"

    hotel = DAILY_HOTEL_ESTIMATE[tier] * days
    food = DAILY_FOOD_ESTIMATE[tier] * days * passengers
    transport = DAILY_TRANSPORT_ESTIMATE[tier] * days
    activities = DAILY_ACTIVITIES_ESTIMATE[tier] * days * passengers

    breakdown = {
        "flights": round(flight_price_total, 2),
        "hotel": round(hotel, 2),
        "food": round(food, 2),
        "transport": round(transport, 2),
        "activities": round(activities, 2),
    }
    breakdown["total"] = round(sum(breakdown.values()), 2)
    breakdown["currency"] = "SAR"
    breakdown["tier"] = tier
    breakdown["is_estimate"] = True
    return breakdown
