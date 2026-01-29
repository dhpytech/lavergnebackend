# entries/filters.py
import django_filters
from django.db.models import Q
from .models import MarisInput


class BaseProductionFilter(django_filters.FilterSet):
    start = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte"
    )
    end = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte"
    )

    shift = django_filters.CharFilter(method="filter_shift")
    productCode = django_filters.CharFilter(method="filter_product_code")

    def filter_shift(self, queryset, name, value):
        if not value or value.lower() in ("total", "all"):
            return queryset
        return queryset.filter(shift=value)

    def filter_product_code(self, queryset, name, value):
        if not value or value.lower() in ("total", "all"):
            return queryset

        return queryset.filter(
            production_data__contains=[{"productCode": value}]
        )


class MarisInputFilter(BaseProductionFilter):
    class Meta:
        model = MarisInput
        fields = ["start", "end", "shift", "productCode"]