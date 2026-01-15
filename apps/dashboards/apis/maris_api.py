from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from dateutil.relativedelta import relativedelta

from ..queries.maris_query import MarisQuery
from ..services.aggregators import ProductionAggregator
from ..services.safety_services import SafetyService
from ..services.statistics import ProductionStats
from ..services.charts import ChartService
from ..queries.maris_query import MarisQuery, FetchParams


class MarisDashboardAPI(APIView):
    def get(self, request):
        start_str = request.GET.get("start")
        end_str = request.GET.get("end")
        shift_val = request.GET.get("shift", "total") # Lấy shift từ request

        # 1. Xác định các mốc thời gian
        start_dt = date.fromisoformat(start_str)
        end_dt = date.fromisoformat(end_str)

        # Tính toán cho LM và LY
        start_lm = start_dt - relativedelta(months=1)
        end_lm = end_dt - relativedelta(months=1)
        start_ly = start_dt - relativedelta(years=1)
        end_ly = end_dt - relativedelta(years=1)

        # 2. Đóng gói tham số vào FetchParams (Để khớp với MarisQuery)
        params_curr = FetchParams(start=start_dt, end=end_dt, shift=shift_val)
        params_lm = FetchParams(start=start_lm, end=end_lm, shift=shift_val)
        params_ly = FetchParams(start=start_ly, end=end_ly, shift=shift_val)

        # 3. Truy vấn sử dụng Object params thay vì truyền rời
        rec_curr = ProductionAggregator.normalize(MarisQuery.fetch_records(params_curr))
        rec_lm = ProductionAggregator.normalize(MarisQuery.fetch_records(params_lm))
        rec_ly = ProductionAggregator.normalize(MarisQuery.fetch_records(params_ly))

        # 4. Lấy dữ liệu An toàn (Giữ nguyên logic của bạn)
        saf_curr = SafetyService.get_summary(start_str, end_str)
        saf_lm = SafetyService.get_summary(start_lm.isoformat(), end_lm.isoformat())
        saf_ly = SafetyService.get_summary(start_ly.isoformat(), end_ly.isoformat())

        # 5. Tính toán KPI & Charts
        stats_service = ProductionStats(rec_curr, rec_lm, rec_ly, saf_curr, saf_lm, saf_ly)
        kpis = stats_service.calculate()
        charts = ChartService.get_production_charts(rec_curr)

        return Response({
            "kpis": kpis,
            "safety": saf_curr,
            "charts": charts,
            "records": rec_curr
        })
