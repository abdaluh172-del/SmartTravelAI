"""
Provider Registry
==================
سجل مركزي لمزودي بيانات الرحلات. لإضافة مزود حقيقي جديد مستقبلًا:

1. أنشئ ملفًا جديدًا في providers/ يطبّق FlightProvider (providers/base.py)
2. استورده هنا وأضفه إلى القاموس PROVIDERS
3. لا حاجة لتغيير أي كود آخر في المشروع - جميع الـ endpoints تستخدم
   get_active_providers() تلقائيًا
"""
from providers.mock_provider import MockFlightProvider

PROVIDERS = {
    "mock": MockFlightProvider(),
    # "amadeus": AmadeusProvider(),      # مثال لمزود حقيقي مستقبلًا
    # "flynas_api": FlynasProvider(),    # مثال لمزود حقيقي مستقبلًا
}


def get_provider(key):
    return PROVIDERS.get(key, PROVIDERS["mock"])


def get_active_providers(config_key="mock"):
    """
    يعيد قائمة المزودين المفعّلين حاليًا. في المرحلة الأولى نستخدم
    Mock Provider فقط، لكن يمكن لاحقًا إعادة هذه الدالة لتعيد عدة
    مزودين حقيقيين في نفس الوقت (لدمج نتائج عدة شركات طيران).
    """
    provider = get_provider(config_key)
    return [provider]
