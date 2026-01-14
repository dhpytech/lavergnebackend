from rest_framework.views import APIView
from rest_framework.response import Response
from ..queries.maris_query import MarisQuery
from ..queries.safety_query import SafetyQuery
from ..services.aggregators import ProductionAggregator
from ..services.statistics import ProductionStats


class MarisDashboardAPI(APIView):
    def get(self, request):
        start = request.GET.get("start")
        end = request.GET.get("end")
        shift = request.GET.get("shift", "total")
        product = request.GET.get("productCode", "total")

        if not start or not end:
            return Response({"error": "Missing dates"}, status=400)

        # 1. Fetch
        qs = MarisQuery.fetch_records(start, end, shift, product)

        # 2. Aggregate & Stats
        normalized = ProductionAggregator.normalize(qs)
        stats_engine = ProductionStats(normalized, start, end)
        kpis = stats_engine.calculate()

        # 3. Thêm dữ liệu Safety
        safety_data = SafetyQuery.count_events(start, end)
        kpis["INCIDENT (TIMES)"] = safety_data["INCIDENT"]
        kpis["ACCIDENT (TIMES)"] = safety_data["ACCIDENT"]

        return Response({
            "kpis": kpis,  # Cho 15 Card
            "records": normalized,  # Cho Modal Audit
            "charts": []  # Có thể thêm ChartGenerator ở đây
        })
