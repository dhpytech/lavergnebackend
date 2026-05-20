from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from entries.models import BaggingInput
from entries.services.bagging_detail_services import BaggingDetailDashboardService


class BaggingEmployeeAnalyticsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        view_type = request.query_params.get('type', 'monthly')
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        if view_type not in ['daily', 'monthly']:
            return Response({"error": "Type must be 'daily' or 'monthly'"}, status=status.HTTP_400_BAD_REQUEST)

        # Lọc Queryset cơ bản theo thời gian
        queryset = BaggingInput.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        result = BaggingDetailDashboardService.get_analytics(queryset, view_type=view_type)
        return Response(result, status=status.HTTP_200_OK)
