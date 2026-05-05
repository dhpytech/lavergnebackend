from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from entries.models import MarisDailySummary


class MarisActiveEmployeesView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        qs = MarisDailySummary.objects.all()
        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])

        employees = qs.values_list('employee', flat=True).distinct().order_by('employee')
        return Response(list(employees))


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
                m_prod=Sum('prod'), m_scrap=Sum('scrap'), m_dlnc=Sum('dlnc'), m_reject=Sum('reject'),
                m_screen=Sum('screen'), m_visslab=Sum('visslab'),
                m_stop_hr=Sum('stop_hr'), m_off_hours=Sum('off_hours'), m_mech_hr=Sum('mech_hr'),
                m_order_chg=Sum('order_chg'), m_mech_fail=Sum('mech_fail'), m_shifts=Sum('num_shifts')
            )
            .order_by('month')
        )

        result = {}
        for item in stats:
            # Chuyển object date thành chuỗi định dạng "2026-04"
            month_str = item['month'].strftime('%Y-%m')
            emp_name = item['employee']

            if month_str not in result:
                result[month_str] = {
                    "SUMMARY": {
                        "total_prod": 0, "total_scrap": 0, "total_dlnc": 0,"total_reject": 0, "total_screen": 0,
                        "total_visslab": 0, "total_shifts": 0, "total_stop_hr": 0, "total_off_hours": 0,
                        "total_mech_hr": 0, "total_order_chg": 0, "total_mech_fail": 0,
                        "net_per_hour": 0, "yield": 0, "oee": 0,
                    },
                    "DETAILS": {}
                }

            result[month_str]["SUMMARY"]["total_prod"] += item['m_prod']
            result[month_str]["SUMMARY"]["total_scrap"] += item['m_scrap']
            result[month_str]["SUMMARY"]["total_dlnc"] += item['m_dlnc']
            result[month_str]["SUMMARY"]["total_reject"] += item['m_reject']
            result[month_str]["SUMMARY"]["total_screen"] += item['m_screen']
            result[month_str]["SUMMARY"]["total_visslab"] += item['m_visslab']
            result[month_str]["SUMMARY"]["total_shifts"] += item['m_shifts']

            result[month_str]["SUMMARY"]["total_stop_hr"] += item['m_stop_hr']
            result[month_str]["SUMMARY"]["total_off_hours"] += item['m_off_hours']
            result[month_str]["SUMMARY"]["total_mech_hr"] += item['m_mech_hr']
            result[month_str]["SUMMARY"]["total_order_chg"] += item['m_order_chg']
            result[month_str]["SUMMARY"]["total_mech_fail"] += item['m_mech_fail']

            result[month_str]["SUMMARY"]["net_per_hour"] = ((result[month_str]["SUMMARY"]["total_prod"] +
                                                            result[month_str]["SUMMARY"]["total_scrap"] +
                                                            result[month_str]["SUMMARY"]["total_reject"]) /
                                                            (result[month_str]["SUMMARY"]["total_shifts"]*12 - result[month_str]["SUMMARY"]["total_stop_hr"]))

            result[month_str]["DETAILS"][emp_name] = \
                {
                "prod": item['m_prod'],
                "scrap": item['m_scrap'],
                "dlnc": item['m_dlnc'],
                "reject": item['m_reject'],
                "screen": item['m_screen'],
                "visslab": item['m_visslab'],

                "stop_hours": item['m_stop_hr'],
                "off_hours": item['m_off_hours'],
                "mech_hr": item['m_mech_hr'],
                "order_chg": item['m_order_chg'],
                "mech_fail": item['m_mech_fail'],

                "shifts": item['m_shifts'],
                }
        # Tính toán các chỉ số KPI USED, YIELD, OEE, MTBF



        return Response(result)
