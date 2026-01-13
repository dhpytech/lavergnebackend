import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from entries.models import MarisInput
from .services.statistics import ProductionStats
from .services.charts import ChartGenerator


class MarisDashboardAPI(APIView):
    def get(self, request):
        start = request.GET.get("start")
        end = request.GET.get("end")
        shift = request.GET.get("shift", "Total")

        qs = MarisInput.objects.filter(date__range=[start, end])
        if shift != "Total":
            qs = qs.filter(shift=shift)

        records = []
        for r in qs:
            records.append({
                "id": r.id,
                "date": r.date,
                "shift": r.shift,
                "employee": r.employee,
                "mainData": r.production_data or [],
                "stopTimes": r.stop_time_data or [],
            })

        stats_service = ProductionStats(
            records,
            datetime.datetime.strptime(start, "%Y-%m-%d").date(),
            datetime.datetime.strptime(end, "%Y-%m-%d").date(),
            MarisInput
        )

        return Response({
            "stats": stats_service.compare_with_previous(),
            "charts": ChartGenerator.generate(qs),
            "results": records
        })
