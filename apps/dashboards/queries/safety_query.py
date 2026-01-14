from safety.models import SafetyTime


class SafetyQuery:
    @staticmethod
    def count_events(start, end):
        qs = SafetyTime.objects.filter(
            date__range=(start, end)
        )
        return {
            "INCIDENT": qs.filter(safety_type="incident").count(),
            "ACCIDENT": qs.filter(safety_type="accident").count(),
        }
