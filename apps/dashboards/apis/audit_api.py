# dashboards/apis/audit_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from ..queries.maris_query import MarisQuery, FetchParams
from ..services.aggregators import ProductionAggregator
import datetime


class AuditAPI(APIView):
    def get(self, request):
        # 1. Thu thập tham số từ URL (Giống Dashboard nhưng tập trung vào chi tiết)
        try:
            params = FetchParams(
                start=datetime.date.fromisoformat(request.GET.get("start")),
                end=datetime.date.fromisoformat(request.GET.get("end")),
                shift=request.GET.get("shift", "total"),
                product_code=request.GET.get("productCode", "total")
            )
        except (TypeError, ValueError):
            return Response({"error": "Invalid dat"
                                      "e format"}, status=400)

        # 2. Lấy dữ liệu từ Query Layer
        qs = MarisQuery.fetch_records(params)

        # 3. Sử dụng Aggregator để làm phẳng dữ liệu
        # Đảm bảo Aggregator trả về đầy đủ: comment, stop_time_data, problem_data...
        records = ProductionAggregator.normalize_all(qs)

        # 4. Trả về kết quả (Có thể thêm phân trang nếu dữ liệu quá lớn)
        return Response({
            "count": len(records),
            "results": records
        })