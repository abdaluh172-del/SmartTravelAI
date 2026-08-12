"""
Mock Flight Provider
=====================
يولّد بيانات رحلات تجريبية (وهمية) بشكل عشوائي لكنه ثابت (deterministic)
اعتمادًا على مدخلات البحث، بحيث تبدو النتائج منطقية ومتّسقة.

هذه البيانات **ليست حقيقية إطلاقًا** ويتم وسمها دائمًا بـ is_mock=True
حتى تعرضها الواجهة الأمامية بوضوح كـ "بيانات تجريبية".

عند توفر API حقيقي لشركة طيران، أنشئ ملفًا جديدًا يطبّق FlightProvider
(مثال: providers/amadeus_provider.py) وسجّله في registry.py بدلاً من
هذا الملف أو بجانبه.
"""
import hashlib
import random
from datetime import datetime, timedelta

from providers.base import FlightProvider

AIRLINES = [
    {"code": "SV", "name": "Saudia", "name_ar": "السعودية"},
    {"code": "XY", "name": "flynas", "name_ar": "طيران ناس"},
    {"code": "F3", "name": "flyadeal", "name_ar": "طيران أديل"},
    {"code": "EK", "name": "Emirates", "name_ar": "طيران الإمارات"},
    {"code": "QR", "name": "Qatar Airways", "name_ar": "القطرية"},
    {"code": "TK", "name": "Turkish Airlines", "name_ar": "الخطوط التركية"},
    {"code": "MS", "name": "EgyptAir", "name_ar": "مصر للطيران"},
    {"code": "GF", "name": "Gulf Air", "name_ar": "طيران الخليج"},
]


class MockFlightProvider(FlightProvider):
    key = "mock"
    is_mock = True

    def _seed(self, *parts):
        s = "-".join(str(p) for p in parts)
        return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16) % (2 ** 32)

    def search(self, origin, destination, depart_date, return_date=None,
               passengers=1, cabin_class="economy"):
        origin = (origin or "").upper().strip()
        destination = (destination or "").upper().strip()
        passengers = max(1, int(passengers or 1))

        rng = random.Random(self._seed(origin, destination, depart_date, cabin_class))
        n_results = rng.randint(6, 10)

        try:
            base_date = datetime.fromisoformat(depart_date)
        except (ValueError, TypeError):
            base_date = datetime.utcnow() + timedelta(days=7)

        cabin_multiplier = {
            "economy": 1.0,
            "premium_economy": 1.6,
            "business": 3.2,
            "first": 5.0,
        }.get(cabin_class, 1.0)

        results = []
        chosen_airlines = rng.sample(AIRLINES, k=min(n_results, len(AIRLINES)))
        while len(chosen_airlines) < n_results:
            chosen_airlines.append(rng.choice(AIRLINES))

        for i, airline in enumerate(chosen_airlines):
            stops = rng.choices([0, 1, 2], weights=[45, 40, 15])[0]
            base_duration = rng.randint(90, 240)  # minutes for a direct-equivalent flight
            duration = base_duration + stops * rng.randint(60, 150)

            base_price = rng.randint(280, 1800)
            stop_discount = {0: 1.15, 1: 1.0, 2: 0.85}[stops]
            price = round(base_price * stop_discount * cabin_multiplier * (1 + 0.08 * (passengers - 1)), 2)

            depart_dt = base_date.replace(
                hour=rng.randint(0, 23), minute=rng.choice([0, 15, 30, 45])
            )
            arrive_dt = depart_dt + timedelta(minutes=duration)

            flight_id = hashlib.md5(
                f"{origin}-{destination}-{depart_date}-{airline['code']}-{i}".encode("utf-8")
            ).hexdigest()[:12]

            results.append({
                "id": flight_id,
                "provider": self.key,
                "airline_code": airline["code"],
                "airline_name": airline["name"],
                "airline_name_ar": airline["name_ar"],
                "logo_url": f"https://images.kiwi.com/airlines/64/{airline['code']}.png",
                "origin": origin,
                "destination": destination,
                "depart_time": depart_dt.isoformat(),
                "arrive_time": arrive_dt.isoformat(),
                "duration_minutes": duration,
                "stops": stops,
                "price": price,
                "currency": "SAR",
                "cabin_class": cabin_class,
                "booking_url": None,
                "is_mock": True,
            })

        return results
