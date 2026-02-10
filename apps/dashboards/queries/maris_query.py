from typing import Literal
from datetime import date
from django.db.models import QuerySet
from entries.models import MarisInput
from dataclasses import dataclass


ShiftType = Literal["total", "day", "night"]
ProductCode = str
EXCLUDE_VALUES = {"total", "all"}


@dataclass(frozen=True)
class FetchParams:
    start: date
    end: date
    shift: ShiftType = "total"
    # product_code: ProductCode = "total"


class MarisQuery:
    @staticmethod
    def fetch_records(p: FetchParams) -> QuerySet[MarisInput]:
        qs = MarisInput.objects.filter(
            date__range=(p.start, p.end)
        )

        if p.shift and p.shift.lower() not in EXCLUDE_VALUES:
            qs = qs.filter(shift__iexact=p.shift)

        # if p.product_code.lower() not in EXCLUDE_VALUES:
        #     qs = qs.filter(production_data__contains=[{"productCode": p.product_code}])

        # 3. Optimize Selection
        return qs.only(
            "id", "date", "shift", "employee",
            "production_data", "stop_time_data", "problem_data"
        ).order_by("-date")
