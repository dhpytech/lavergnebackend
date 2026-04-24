from rest_framework.views import APIView
from rest_framework.response import Response
from entries.selectors.bagging_selectors import get_bagging_entries_selector
from entries.services.bagging_aggregate_services import BaggingAggregateService


class BaggingDashboardAPI(APIView):
    def get(self, request):
        filters = {
            'start_date': request.query_params.get('start'),
            'end_date': request.query_params.get('end'),
            'shift': request.query_params.get('shift'),
            'lot_number': request.query_params.get('lot')
        }

        # 1. Selector lấy data hiện tại
        queryset = get_bagging_entries_selector(
            start_date=filters['start_date'],
            end_date=filters['end_date'],
            shift=filters['shift'],
            lot_number=filters['lot_number']
        )

        # 2. Service xử lý kèm theo so sánh quá khứ
        data = BaggingAggregateService.aggregate_production_data(queryset, filters)

        return Response(data)
