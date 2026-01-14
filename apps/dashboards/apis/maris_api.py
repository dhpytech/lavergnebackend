# dashboards/apis/maris_api.py
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response

from dashboards.queries.maris_query import MarisQuery
from dashboards.services.aggregators import ProductionAggregator
from dashboards.services.statistics import ProductionStats
from dashboards.services.charts import ChartGenerator


class MarisDashboardAPI(APIView):

    def get(self, request):
        start = request.GET.get("start")
        end = request.GET.get("end")
        shift = request.GET.get("shift", "total")
        product = request.GET.get("productCode", "total")

        if not start or not end:
            return Response(
                {"error": "start and end are required"},
                status=400
            )

        start_date = datetime.date.fromisoformat(start)
        end_date = datetime.date.fromisoformat(end)

        qs = MarisQuery.fetch_records(
            start_date, end_date, shift, product
        )

        records = []
        for r in qs:
            for item in r.production_data:
                records.append(
                    ProductionAggregator.normalize_record({
                        "date": r.date,
                        "shift": r.shift,
                        "employee": r.employee,
                        "mainData": item,
                        "stopTimes": r.stop_time_data or [],
                        "problems": r.problem_data or []
                    })
                )

        stats = ProductionStats(records)

        return Response({
            "kpis": stats.kpis(),
            "problems": stats.problems(),
            "charts": {
                "byDate": ChartGenerator.by_date(records)
            },
            "records": records
        })
