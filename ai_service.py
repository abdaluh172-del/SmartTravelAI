"""
AI Service
==========
طبقة وسيطة بين Routes ومزودي الذكاء الاصطناعي.

    Routes -> AIService -> AIProvider (Mock أو Anthropic أو أي مزود آخر لاحقًا)

هذا يسمح بتبديل مزود الذكاء الاصطناعي بالكامل (مثلًا من Mock إلى مزود
حقيقي، أو من مزود إلى آخر) دون تغيير أي كود في الـ routes.
"""
from services.ai_providers.mock_ai_provider import MockAIProvider


class AIService:
    def __init__(self, app_config):
        self.config = app_config
        self._provider = self._build_provider()

    def _build_provider(self):
        provider_name = self.config.get("AI_PROVIDER", "mock")
        api_key = self.config.get("ANTHROPIC_API_KEY", "")

        if provider_name == "anthropic" and api_key:
            try:
                from services.ai_providers.anthropic_provider import AnthropicAIProvider
                return AnthropicAIProvider(api_key, self.config.get("AI_MODEL", "claude-sonnet-4-6"))
            except Exception:
                # في حال فشل تحميل المزود الحقيقي، لا نعطل النظام أبدًا
                return MockAIProvider()

        # الوضع الافتراضي: تجريبي بالكامل، يعمل دائمًا بدون أي مفتاح
        return MockAIProvider()

    @property
    def is_mock(self):
        return self._provider.is_mock

    def get_popular_places(self, destination):
        provider = self._provider
        if hasattr(provider, "get_popular_places"):
            return provider.get_popular_places(destination)
        return MockAIProvider().get_popular_places(destination)

    def generate_itinerary(self, destination, days, budget, trip_type, interests):
        return self._provider.generate_itinerary(destination, days, budget, trip_type, interests)

    def compare_flights(self, flight_a, flight_b):
        return self._provider.compare_flights(flight_a, flight_b)

    def free_text_plan(self, prompt_text, context=None):
        return self._provider.free_text_plan(prompt_text, context)
