# dashboards/queries/maris.py
from entries.models import MarisInput


class MarisQuery:
    @staticmethod
    def fetch_records(
        start,
        end,
        shift="total",
        product_code="total"
    ):
        qs = MarisInput.objects.filter(
            date__gte=start,
            date__lte=end,
        )

        if shift.lower() not in ("total", "all"):
            qs = qs.filter(shift=shift)

        if product_code.lower() not in ("total", "all"):
            qs = qs.filter(
                production_data__contains=[
                    {"productCode": product_code}
                ]
            )

        return qs.only(
            "id",
            "date",
            "shift",
            "employee",
            "production_data",
            "stop_time_data",
            "problem_data"
        )
