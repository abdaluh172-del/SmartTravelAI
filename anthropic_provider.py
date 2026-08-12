"""
Anthropic AI Provider (اختياري)
=================================
يُستخدم فقط عند توفر ANTHROPIC_API_KEY في متغيرات البيئة على السيرفر.
المفتاح لا يصل أبدًا إلى الواجهة الأمامية - يُستخدم فقط هنا داخل Backend.

إذا فشل الاتصال أو لم يوجد مفتاح، يجب أن يتم استخدام MockAIProvider بدلًا
من هذا الملف (يتم ذلك تلقائيًا في services/ai_service.py).
"""
import json

import requests

from services.ai_providers.base import AIProvider
from services.ai_providers.mock_ai_provider import MockAIProvider

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicAIProvider(AIProvider):
    key = "anthropic"
    is_mock = False

    def __init__(self, api_key, model="claude-sonnet-4-6"):
        self.api_key = api_key
        self.model = model
        self._fallback = MockAIProvider()

    def _call(self, system_prompt, user_prompt, max_tokens=1500):
        try:
            resp = requests.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            text_parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
            return "\n".join(text_parts)
        except Exception:
            return None

    def generate_itinerary(self, destination, days, budget, trip_type, interests):
        system = (
            "أنت مخطط رحلات سياحي خبير. أعد فقط كائن JSON صالح بدون أي نص إضافي "
            "بالمفاتيح: destination, days, daily_plan (قائمة بها day, title, blocks[{time, activity}]), "
            "budget_breakdown (flights, hotel, food, transport, activities), total_estimated_budget, currency."
        )
        user = (
            f"الوجهة: {destination}\nعدد الأيام: {days}\nالميزانية: {budget} ريال سعودي\n"
            f"نوع الرحلة: {trip_type}\nالاهتمامات: {interests}"
        )
        raw = self._call(system, user)
        if not raw:
            return self._fallback.generate_itinerary(destination, days, budget, trip_type, interests)
        try:
            cleaned = raw.strip().strip("```").replace("json\n", "", 1)
            parsed = json.loads(cleaned)
            parsed["is_mock"] = False
            return parsed
        except Exception:
            result = self._fallback.generate_itinerary(destination, days, budget, trip_type, interests)
            result["note"] = "تعذر تحليل استجابة الذكاء الاصطناعي، تم استخدام الخطة الاحتياطية."
            return result

    def compare_flights(self, flight_a, flight_b):
        system = "أنت مساعد سفر. قارن بين رحلتين بإيجاز بالعربية وأعد الرد كنص عادي فقط."
        user = json.dumps({"flight_a": flight_a, "flight_b": flight_b}, ensure_ascii=False)
        raw = self._call(system, user, max_tokens=400)
        if not raw:
            return self._fallback.compare_flights(flight_a, flight_b)
        return {"recommendation": raw, "is_mock": False}

    def free_text_plan(self, prompt_text, context=None):
        system = (
            "أنت مساعد تخطيط رحلات. حلل طلب المستخدم بالنص الحر واستخرج منه الوجهة وعدد الأيام "
            "والميزانية ونوع الرحلة والاهتمامات، ثم أعد فقط JSON بنفس شكل خطة الرحلة اليومية "
            "بالمفاتيح: destination, days, daily_plan, budget_breakdown, total_estimated_budget, currency."
        )
        raw = self._call(system, prompt_text)
        if not raw:
            return self._fallback.free_text_plan(prompt_text, context)
        try:
            cleaned = raw.strip().strip("```").replace("json\n", "", 1)
            parsed = json.loads(cleaned)
            parsed["is_mock"] = False
            parsed["source_prompt"] = prompt_text
            return parsed
        except Exception:
            result = self._fallback.free_text_plan(prompt_text, context)
            result["note"] = "تعذر تحليل استجابة الذكاء الاصطناعي، تم استخدام الخطة الاحتياطية."
            return result
