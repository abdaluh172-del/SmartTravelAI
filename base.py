from abc import ABC, abstractmethod


class AIProvider(ABC):
    key = "base"
    is_mock = True

    @abstractmethod
    def generate_itinerary(self, destination, days, budget, trip_type, interests):
        """يعيد dict يحتوي itinerary (قائمة أيام)، وملخص، وميزانية تقريبية."""
        raise NotImplementedError

    @abstractmethod
    def compare_flights(self, flight_a, flight_b):
        """يعيد نص توصية يقارن بين رحلتين."""
        raise NotImplementedError

    @abstractmethod
    def free_text_plan(self, prompt_text, context=None):
        """يحلل طلب المستخدم بالنص الحر وينشئ خطة رحلة كاملة."""
        raise NotImplementedError
