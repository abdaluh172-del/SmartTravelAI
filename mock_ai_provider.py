"""
Mock AI Provider
=================
مزود ذكاء اصطناعي "تجريبي" قائم على قواعد بسيطة (Rule-Based) بدلًا من
نموذج لغوي حقيقي. يُستخدم تلقائيًا عندما لا يوجد ANTHROPIC_API_KEY
حتى لا يتعطل النظام أبدًا. النتائج منطقية لكنها ليست ذكاءً اصطناعيًا
حقيقيًا، ويتم وسمها بـ is_mock=True في كل استجابة.
"""
import random

from services.ai_providers.base import AIProvider

PLACE_TEMPLATES = {
    "default": [
        "المتحف الوطني", "السوق التاريخي القديم", "الحديقة المركزية",
        "برج المدينة", "الواجهة البحرية / النهرية", "الحي الثقافي",
        "معلم ديني بارز", "منطقة المطاعم الشعبية", "مركز تسوق حديث",
        "متحف فني", "حديقة حيوانات أو أكواريوم", "جولة مشي في البلدة القديمة",
    ]
}

ACTIVITY_BY_TYPE = {
    "عائلية": ["حديقة ترفيهية", "أكواريوم", "متحف تفاعلي للأطفال", "نزهة عائلية على الشاطئ"],
    "فردية": ["جولة تصوير حرة", "مقهى مطل على المدينة", "مسار مشي أو دراجات", "زيارة معرض فني"],
    "أصدقاء": ["نشاط مغامرات (كاياك/تسلق)", "جولة حياة ليلية", "لعبة جماعية أو تجربة ترفيهية", "رحلة يخت قصيرة"],
    "عمل": ["اجتماع في مقهى عمل هادئ", "مساحة عمل مشترك", "عشاء عمل في مطعم راقٍ", "وقت حر مسائي"],
}

MEAL_SUGGESTIONS = [
    "مطعم محلي مشهور بالمأكولات التقليدية",
    "مطعم مأكولات بحرية",
    "مقهى شهير للفطور",
    "مطعم عالمي متوسط التكلفة",
    "تجربة طعام الشارع المحلي",
    "مطعم فاخر لتجربة خاصة",
]


class MockAIProvider(AIProvider):
    key = "mock"
    is_mock = True

    def _rng(self, *parts):
        seed = "-".join(str(p) for p in parts)
        return random.Random(hash(seed) % (2 ** 32))

    def get_popular_places(self, destination):
        rng = self._rng("places", destination)
        places = PLACE_TEMPLATES["default"][:]
        rng.shuffle(places)
        return places[:8]

    def generate_itinerary(self, destination, days, budget, trip_type, interests):
        days = max(1, min(int(days or 3), 30))
        rng = self._rng("itin", destination, days, budget, trip_type, interests)
        places = PLACE_TEMPLATES["default"][:]
        rng.shuffle(places)
        activities = ACTIVITY_BY_TYPE.get(trip_type, ACTIVITY_BY_TYPE["فردية"])

        daily_plan = []
        place_idx = 0
        for day in range(1, days + 1):
            if day == 1:
                blocks = [
                    {"time": "الوصول", "activity": "الوصول إلى المطار والتوجه للفندق"},
                    {"time": "الظهر", "activity": rng.choice(MEAL_SUGGESTIONS)},
                    {"time": "بعد الظهر", "activity": places[place_idx % len(places)]},
                    {"time": "المساء", "activity": rng.choice(MEAL_SUGGESTIONS)},
                ]
                place_idx += 1
            elif day == days and days > 1:
                blocks = [
                    {"time": "الصباح", "activity": places[place_idx % len(places)]},
                    {"time": "الظهر", "activity": rng.choice(MEAL_SUGGESTIONS)},
                    {"time": "بعد الظهر", "activity": "تسوق وشراء الهدايا التذكارية"},
                    {"time": "المساء", "activity": "التوجه إلى المطار للمغادرة"},
                ]
                place_idx += 1
            else:
                blocks = [
                    {"time": "الصباح", "activity": places[place_idx % len(places)]},
                    {"time": "الظهر", "activity": rng.choice(MEAL_SUGGESTIONS)},
                    {"time": "بعد الظهر", "activity": rng.choice(activities)},
                    {"time": "المساء", "activity": rng.choice(MEAL_SUGGESTIONS)},
                ]
                place_idx += 1

            daily_plan.append({"day": day, "title": f"اليوم {day}", "blocks": blocks})

        budget_val = float(budget) if budget else days * 700.0
        breakdown = self._budget_breakdown(budget_val, days)

        return {
            "destination": destination,
            "days": days,
            "trip_type": trip_type,
            "interests": interests,
            "daily_plan": daily_plan,
            "budget_breakdown": breakdown,
            "total_estimated_budget": round(sum(breakdown.values()), 2),
            "currency": "SAR",
            "is_mock": True,
            "note": "بيانات تجريبية تم إنشاؤها بواسطة مساعد السفر (وضع تجريبي بدون مزود ذكاء اصطناعي خارجي).",
        }

    def _budget_breakdown(self, total_budget, days):
        # نسب تقديرية شائعة لتوزيع ميزانية سفر
        ratios = {
            "flights": 0.30,
            "hotel": 0.30,
            "food": 0.18,
            "transport": 0.10,
            "activities": 0.12,
        }
        return {k: round(total_budget * v, 2) for k, v in ratios.items()}

    def compare_flights(self, flight_a, flight_b):
        price_diff = round(flight_b["price"] - flight_a["price"], 2)
        time_diff = flight_a["duration_minutes"] - flight_b["duration_minutes"]
        stops_diff = flight_a["stops"] - flight_b["stops"]

        notes = []
        if price_diff > 0 and (time_diff > 0 or stops_diff > 0):
            notes.append(
                f"الرحلة الثانية أغلى بـ {abs(price_diff)} {flight_a.get('currency','SAR')} "
                f"لكنها أسرع بـ {abs(time_diff)} دقيقة وعدد توقفاتها أقل بـ {abs(stops_diff)}."
                if time_diff > 0 else
                f"الرحلة الثانية أغلى بـ {abs(price_diff)} {flight_a.get('currency','SAR')}."
            )
            if time_diff > 90 or stops_diff >= 1:
                notes.append("مقابل فرق السعر، الرحلة الثانية قد تستحق التكلفة الإضافية بسبب توفير الوقت وقلة التوقفات.")
            else:
                notes.append("الفرق في الوقت بسيط نسبيًا، لذا قد تكون الرحلة الأولى ذات قيمة أفضل من ناحية التكلفة.")
        elif price_diff < 0:
            notes.append(
                f"الرحلة الثانية أرخص بـ {abs(price_diff)} {flight_a.get('currency','SAR')}."
            )
            if time_diff < 0:
                notes.append("وهي أيضًا أبطأ قليلًا، لكنها تظل الخيار الأفضل من ناحية القيمة الإجمالية.")
            else:
                notes.append("وهي كذلك أسرع أو مساوية، ما يجعلها الخيار الأفضل بوضوح.")
        else:
            notes.append("الرحلتان متقاربتان جدًا في السعر، لذا يمكن الاختيار بناءً على وقت المغادرة المفضل.")

        return {
            "recommendation": " ".join(notes),
            "price_difference": price_diff,
            "duration_difference_minutes": time_diff,
            "is_mock": True,
        }

    def free_text_plan(self, prompt_text, context=None):
        context = context or {}
        destination = context.get("destination", "الوجهة المختارة")
        days = context.get("days", 5)
        budget = context.get("budget", 5000)
        trip_type = context.get("trip_type", "فردية")
        interests = context.get("interests", "سياحة عامة")

        itinerary = self.generate_itinerary(destination, days, budget, trip_type, interests)
        itinerary["source_prompt"] = prompt_text
        return itinerary
