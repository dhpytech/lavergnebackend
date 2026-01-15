from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date

# Import các thành phần nội bộ đã thống nhất
from ..queries.maris_query import MarisQuery
from ..services.aggregators import ProductionAggregator


class MarisAuditAPI(APIView):
    """
    API cung cấp dữ liệu chi tiết (Audit Log) cho Modal khi người dùng
    tương tác với các chỉ số hoặc biểu đồ trên Dashboard.
    """

    def get(self, request):
        try:
            # 1. Tiếp nhận tham số từ request
            start_p = request.GET.get("start")
            end_p = request.GET.get("end")
            shift = request.GET.get("shift", "total")
            product_code = request.GET.get("product_code")

            if not start_p or not end_p:
                return Response(
                    {"error": "Vui lòng cung cấp tham số start và end (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Truy vấn dữ liệu thô thông qua Query Layer
            qs = MarisQuery.fetch_records(
                date.fromisoformat(start_p),date.fromisoformat(end_p),shift
            )

            # 3. Chuẩn hóa dữ liệu thông qua Aggregator đã thống nhất
            records = ProductionAggregator.normalize(qs)

            # 4. Lọc bổ sung theo Product Code nếu có yêu cầu từ biểu đồ
            if product_code:
                records = [r for r in records if r['productCode'] == product_code]

            return Response({
                "count": len(records),
                "audit_logs": records
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": f"Định dạng ngày không hợp lệ: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
