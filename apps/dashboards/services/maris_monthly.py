from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from entries.models import MarisDailySummary


class MarisMonthlyAnalyticsView(APIView):
    def get(self, request):
        selected_employees = request.query_params.get('employees')
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        qs = MarisDailySummary.objects.all()

        if selected_employees:
            emp_list = selected_employees.split(',')
            qs = qs.filter(employee__in=emp_list)

        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])






        stats = (
            qs.annotate(month=TruncMonth('date'))
            .values('month', 'employee')
            .annotate(
                m_prod=Sum('prod'),
                m_scrap=Sum('scrap'),
                m_shifts=Sum('num_shifts')
            )
            .order_by('month')
        )

        # 5. Cấu trúc lại dữ liệu (Nested Dictionary)
        result = {}
        for item in stats:
            # Chuyển object date thành chuỗi định dạng "2026-04"
            month_str = item['month'].strftime('%Y-%m')
            emp_name = item['employee']

            if month_str not in result:
                result[month_str] = {
                    "SUMMARY": {"total_prod": 0, "total_scrap": 0, "total_shifts": 0},
                    "DETAILS": {}
                }

            # Cộng dồn vào mục SUMMARY của tháng (Trend tổng cả xưởng)
            result[month_str]["SUMMARY"]["total_prod"] += item['m_prod']
            result[month_str]["SUMMARY"]["total_scrap"] += item['m_scrap']
            result[month_str]["SUMMARY"]["total_shifts"] += item['m_shifts']

            # Gán vào mục DETAILS (Dữ liệu riêng của từng người để lọc)
            result[month_str]["DETAILS"][emp_name] = {
                "prod": item['m_prod'],
                "scrap": item['m_scrap'],
                "shifts": item['m_shifts'],
                "efficiency": round((item['m_prod'] / (item['m_prod'] + item['m_scrap']) * 100), 2) if (item['m_prod'] +
                                                                                                        item[
                                                                                                            'm_scrap']) > 0 else 0
            }

        return Response(result)