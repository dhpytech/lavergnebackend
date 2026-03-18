from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date

# Import các thành phần nội bộ đã thống nhất
from ..queries.maris_query import MarisQuery
from ..services.aggregators import ProductionAggregator


class MarisAuditAPI(APIView):
    def get(self, request):
        try:
            start_p = request.GET.get("start")
            end_p = request.GET.get("end")
            shift = request.GET.get("shift", "total")
            product_code = request.GET.get("product_code")

            if not start_p or not end_p:
                return Response(
                    {"error": "Vui lòng cung cấp tham số start và end (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            qs = MarisQuery.fetch_records(
                date.fromisoformat(start_p), date.fromisoformat(end_p), shift, product_code
            )

            records = ProductionAggregator.normalize(qs)

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
