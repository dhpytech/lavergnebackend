from rest_framework import viewsets
from .models import MarisInput, MetalInput, BaggingInput
from .serializers import MarisInputSerializer, MetalInputSerializer, BaggingInputSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MarisInputFilter


# 1. Maris ViewSet
class MarisInputViewSet(viewsets.ModelViewSet):
    queryset = MarisInput.objects.all()
    serializer_class = MarisInputSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MarisInputFilter

    # filterset_fields = {
    #     'date': ['gte', 'lte'],
    # }


# 2. Metal ViewSet
class MetalInputViewSet(viewsets.ModelViewSet):
    queryset = MetalInput.objects.all()
    serializer_class = MetalInputSerializer


# 3. Bagging ViewSet
class BaggingInputViewSet(viewsets.ModelViewSet):
    queryset = BaggingInput.objects.all()
    serializer_class = BaggingInputSerializer


import calendar
from django.utils import timezone
# from rest_framework import viewsets
from rest_framework.response import Response
from collections import defaultdict
# from .models import MarisInput
# from .serializers import MarisInputSerializer
# from .filters import MarisInputFilter


class IsoMonthlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MarisInput.objects.all().order_by('date')
    serializer_class = MarisInputSerializer
    filterset_class = MarisInputFilter

    def list(self, request, *args, **kwargs):
        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = int(request.query_params.get('year', timezone.now().year))
        except ValueError:
            return Response({"error": "Invalid month/year"}, status=400)

        _, last_day = calendar.monthrange(year, month)

        # 1. Lấy dữ liệu qua Filter
        query_params = request.query_params.copy()
        query_params.update({'start': f"{year}-{month:02d}-01", 'end': f"{year}-{month:02d}-{last_day}"})
        filtered_qs = MarisInputFilter(query_params, queryset=self.get_queryset()).qs

        # 2. Khởi tạo Ma trận (Index 0 = Ngày 1)
        matrix = {
            "production": defaultdict(lambda: [0] * last_day),
            "scrap": defaultdict(lambda: [0] * last_day),
            "downtime": defaultdict(lambda: [0] * last_day),
            "problems": defaultdict(lambda: [""] * last_day),
            "operators": defaultdict(lambda: [""] * last_day)
        }

        # 3. Flatten dữ liệu
        for rec in filtered_qs:
            day_idx = rec.date.day - 1

            # Operator
            matrix["operators"]["Main Line"][day_idx] = rec.employee or ""

            # Production & Scrap
            for p in rec.production_data:
                sku = p.get('productCode', 'N/A')
                matrix["production"][sku][day_idx] += float(p.get('goodPro', 0))
                matrix["scrap"][sku][day_idx] += float(p.get('scrap', 0))

            # Stop Time (Downtime) - Quan trọng để hiện chi tiết lỗi
            for stop in getattr(rec, 'stop_time_data', []):
                reason = stop.get('reason', 'Others')
                matrix["downtime"][reason][day_idx] += float(stop.get('duration', 0))

            # Problems
            for prob in getattr(rec, 'problem_data', []):
                p_type = prob.get('type', 'Others')
                matrix["problems"][p_type][day_idx] = "1"  # Hoặc text mô tả

        return Response({
            "metadata": {"month": month, "year": year, "last_day": last_day},
            "matrix": matrix
        })

