# dashboards/apis/maris_api.py
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from entries.models import MarisInput
from .services.statistics import ProductionStats
from .services.charts import ChartGenerator


class MarisDashboardAPI(APIView):
    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        qs = MarisInput.objects.filter(date__range=[start_date, end_date])
        records = [r.__dict__ for r in qs]

        stats_service = ProductionStats(records, start_date, end_date, MarisInput)
        stats_with_compare = stats_service.compare_with_previous()
        charts = ChartGenerator.generate(qs)

        return Response({
            "stats": stats_with_compare,
            "charts": charts,
        })
