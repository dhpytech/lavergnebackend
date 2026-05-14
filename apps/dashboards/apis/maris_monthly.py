from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from entries.models import MarisDailySummary
from types import SimpleNamespace


SUMMARY_CONFIGS = [
    {
        "id": "TOTAL_PROD",
        "title": "PRODUCTION TREND LINE CHART",
        "menuTitle": "PRODUCTION",
        "chartStatus": "Active",
        "datasets": [{"label": "PRODUCTION (kg)", "dataPath": "SUMMARY.total_prod", "borderColor": "#3b82f6",
                      "backgroundColor": "rgba(59, 130, 246, 0.05)", "fill": True}]
    },
    {
        "id": "TOTAL_SCRAP",
        "title": "SCRAP TREND LINE CHART",
        "menuTitle": "SCRAP",
        "chartStatus": "Active",
        "datasets": [{"label": "SCRAP (kg)", "dataPath": "SUMMARY.total_scrap", "borderColor": "#ef4444",
                      "backgroundColor": "rgba(239, 68, 68, 0.05)", "fill": True}]
    },
    {
        "id": "TOTAL_DLNC",
        "title": "DLNC TREND LINE CHART",
        "menuTitle": "DLNC",
        "chartStatus": "Active",
        "datasets": [{"label": "DLNC (kg)", "dataPath": "SUMMARY.total_dlnc", "borderColor": "#f59e0b",
                      "backgroundColor": "rgba(245, 158, 11, 0.05)", "fill": True}]
    },
    {
        "id": "TOTAL_REJECT",
        "title": "REJECT TREND LINE CHART",
        "menuTitle": "REJECT",
        "chartStatus": "Active",
        "datasets": [{"label": "REJECT (kg)", "dataPath": "SUMMARY.total_reject", "borderColor": "#ef4444",
                      "backgroundColor": "rgba(239, 68, 68, 0.05)", "fill": True}]
    },
    {
        "id": "TOTAL_SCREEN",
        "title": "SCREEN TREND LINE CHART",
        "menuTitle": "SCREEN",
        "chartStatus": "Active",
        "datasets": [{"label": "SCREEN (kg)", "dataPath": "SUMMARY.total_screen", "borderColor": "#3b82f6",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "TOTAL_VISSLAB",
        "title": "VISSLAB TREND LINE CHART",
        "menuTitle": "VISSLAB",
        "chartStatus": "Active",
        "datasets": [{"label": "VISSLAB (kg)", "dataPath": "SUMMARY.total_visslab", "borderColor": "#6366f1",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "TOTAL_SHIFTS",
        "title": "TOTAL SHIFTS CHART",
        "menuTitle": "SHIFTS",
        "chartStatus": "Active",
        "datasets": [{"label": "SHIFTS", "dataPath": "SUMMARY.total_shifts", "borderColor": "#64748b",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "NET_PER_HOUR",
        "title": "NET PER HOUR ANALYSIS",
        "menuTitle": "NET PER HOUR",
        "chartStatus": "Active",
        "datasets": [{"label": "kg/hour", "dataPath": "SUMMARY.net_per_hour", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "USED",
        "title": "% USED",
        "menuTitle": "% USED",
        "chartStatus": "Active",
        "datasets": [{"label": "%", "dataPath": "SUMMARY.used", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "YIELD",
        "title": "YIELD",
        "menuTitle": "YIELD",
        "chartStatus": "Active",
        "datasets": [{"label": "%", "dataPath": "SUMMARY.yield", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "OEE",
        "title": "OEE",
        "menuTitle": "OEE",
        "chartStatus": "Active",
        "datasets": [{"label": "%", "dataPath": "SUMMARY.oee", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "PERFECT_TIME",
        "title": "PERFECT_TIME",
        "menuTitle": "PERFECT_TIME",
        "chartStatus": "Active",
        "datasets": [{"label": "%", "dataPath": "SUMMARY.total_perfect_time", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "MTTR",
        "title": "MTTR",
        "menuTitle": "MTTR",
        "chartStatus": "Active",
        "datasets": [{"label": "hour", "dataPath": "SUMMARY.mttr", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    },
    {
        "id": "MTBF",
        "title": "MTBF",
        "menuTitle": "MTBF",
        "chartStatus": "Active",
        "datasets": [{"label": "hour", "dataPath": "SUMMARY.mtbf", "borderColor": "#10b981",
                      "backgroundColor": "transparent", "fill": False}]
    }
]


class Metric:
    prod = "prod"
    scrap = "scrap"
    dlnc = "dlnc"
    reject = "reject"
    screen = "screen"
    visslab = "visslab"
    stop_hours = "stop_hr"
    off_hours = "off_hours"
    mech_hr = "mech_hr"
    order_chg = "order_chg"
    mech_fail = "mech_fail"
    shifts = "shifts"
    runtime = "runtime"
    net_hour = "net_hour"
    used = "used"
    percent_yield = "percent_yield"
    oee = "oee"
    mttr = "mttr"
    perfect_time = "perfect_time"


METRIC_CONFIGS = [
    {
        "id": "PROD",
        "label": "PRODUCTION (KG)",
        "path": "prod",
        "color": "#3b82f6",
        "chartStatus": "Active"
    },
    {
        "id": "SCRAP",
        "label": "SCRAP (KG)",
        "path": "scrap",
        "color": "#ef4444",
        "chartStatus": "Active"
    },
    {
        "id": "DLNC",
        "label": "DLNC (KG)",
        "path": "dlnc",
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "REJECT",
        "label": "REJECT (KG)",
        "path": "reject",
        "color": "#f59e0b",
        "chartStatus": "Active"
    },
    {
        "id": "SCREEN_CHANGER",
        "label": "SCREEN CHANGER (KG)",
        "path": "screen",
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "VISSLAB",
        "label": "VISSLAB (KG)",
        "path": "visslab",
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "shifts",
        "label": "NUM_SHIFTS (shift)",
        "path": Metric.shifts,
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "STOP_TIME",
        "label": "STOP TIME (HOUR)",
        "path": "stop_hr",
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "OFF_TIME",
        "label": "OFF_TIME (HOUR)",
        "path": "off_hours",
        "color": "#8b5cf6",
        "chartStatus": "DisActive"
    },
    {
        "id": "MECH_HOUR",
        "label": "TIME OF FAILURE (HOUR)",
        "path": "mech_hr",
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "ORDER_CHANGE",
        "label": "NUM OF ORDER CHANGE (TIME)",
        "path": "order_chg",
        "color": "#8b5cf6",
        "chartStatus": "Active"
    },
    {
        "id": "MECH_FAILURE",
        "label": "NUM OF FAILURE (TIME)",
        "path": Metric.mech_fail,
        "chartStatus": "Active"
    },
    {
        "id": "net_hour",
        "label": "NET PER HOUR (kg/hour)",
        "path": Metric.net_hour,
        "chartStatus": "Active"
    },
    {
        "id": "used",
        "label": "% USED (%)",
        "path": Metric.used,
        "chartStatus": "Active"
    },
    {
        "id": "percent_yield",
        "label": "% YIELD (%)",
        "path": Metric.percent_yield,
        "chartStatus": "Active"
    },
    {
        "id": "oee",
        "label": "OEE (%)",
        "path": Metric.oee,
        "chartStatus": "Active"
    },
    {
        "id": "perfect_time",
        "label": "PERFECT TIME (HOUR)",
        "path": Metric.perfect_time,
        "chartStatus": "Active"
    },
    {
        "id": "mttr",
        "label": "MTTR (HOUR)",
        "path": Metric.mttr,
        "chartStatus": "Active"
    },
]


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
                m_screen=Sum('screen'), m_visslab=Sum('visslab'), m_output_setting=Sum('output_setting'),
                m_stop_hr=Sum('stop_hr'), m_off_hours=Sum('off_hours'), m_mech_hr=Sum('mech_hr'),
                m_order_chg=Sum('order_chg'), m_mech_fail=Sum('mech_fail'), m_shifts=Sum('num_shifts'),
                m_perfect_time=Sum('perfect_time')
            )
            .order_by('month')
        )

        result = {}
        for item in stats:
            month_str = item['month'].strftime('%Y-%m')
            emp_name = item['employee']

            if month_str not in result:
                result[month_str] = {
                    "SUMMARY": {
                        "total_prod": 0, "total_scrap": 0, "total_dlnc": 0, "total_reject": 0, "total_screen": 0,
                        "total_visslab": 0, "total_shifts": 0, "total_stop_hr": 0, "total_off_hours": 0,
                        "total_mech_hr": 0, "total_order_chg": 0, "total_mech_fail": 0, "total_output_setting": 0,
                        "net_per_hour": 0, "used": 0, "yield": 0, "oee": 0, "mttr": 0, "mtbf": 0, "total_perfect_time": 0
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
            result[month_str]["SUMMARY"]["total_output_setting"] += item['m_output_setting']
            result[month_str]["SUMMARY"]["total_perfect_time"] += item['m_perfect_time']

            t_shift_time = result[month_str]["SUMMARY"]["total_shifts"]*12
            t_stop_time_no_weekend = result[month_str]["SUMMARY"]["total_stop_hr"] - result[month_str]["SUMMARY"]["total_off_hours"]
            t_runtime = t_shift_time - t_stop_time_no_weekend
            t_output = (result[month_str]["SUMMARY"]["total_prod"] + result[month_str]["SUMMARY"]["total_scrap"] +
                        result[month_str]["SUMMARY"]["total_reject"])
            t_input = (result[month_str]["SUMMARY"]["total_prod"] + result[month_str]["SUMMARY"]["total_scrap"] +
                       result[month_str]["SUMMARY"]["total_reject"] + result[month_str]["SUMMARY"]["total_visslab"])

            t_net_per_hour = t_output/t_runtime if t_runtime else 0
            t_used = t_runtime/t_shift_time
            t_percent_yield = result[month_str]["SUMMARY"]["total_prod"]/t_input if t_input else 0
            t_mttr = result[month_str]["SUMMARY"]["total_mech_hr"]/result[month_str]["SUMMARY"]["total_mech_fail"] if result[month_str]["SUMMARY"]["total_mech_fail"] else 0
            t_mtbf = t_shift_time/result[month_str]["SUMMARY"]["total_mech_fail"] if result[month_str]["SUMMARY"]["total_mech_fail"] else 0

            t_rate = result[month_str]["SUMMARY"]["total_perfect_time"]/t_runtime if t_runtime else 0
            t_oee = t_used * t_percent_yield * t_rate

            result[month_str]["SUMMARY"]["net_per_hour"] = t_net_per_hour
            result[month_str]["SUMMARY"]["mttr"] = t_mttr
            result[month_str]["SUMMARY"]["mtbf"] = t_mtbf

            result[month_str]["SUMMARY"]["used"] = t_used
            result[month_str]["SUMMARY"]["yield"] = t_percent_yield
            result[month_str]["SUMMARY"]["oee"] = t_oee

            sh = item.get('m_shifts', 0) or 0
            st = item.get('m_stop_hr', 0) - item.get('m_off_hours')

            e_runtime = sh * 12 - st
            e_output = item.get('m_prod', 0) + item.get('m_scrap', 0) + item.get('m_reject', 0)
            e_input = item.get('m_prod', 0) + item.get('m_scrap', 0) + item.get('m_reject', 0) + item.get('m_visslab', 0)
            e_perfect_time = item.get("m_perfect_time")

            e_net_hour = e_output / e_runtime if e_runtime > 0 else 0
            e_used = e_runtime / (sh*12) if sh > 0 else 0
            e_percent_yield = item.get('m_prod', 0) / e_input if e_input > 0 else 0
            e_mttr = item.get('m_mech_hr', 0) / item.get('m_mech_fail', 0) if item.get('m_mech_hr', 0) > 0 else 0

            e_rate = e_perfect_time/e_runtime if e_runtime > 0 else 0
            e_oee = e_used * e_percent_yield * e_rate

            result[month_str]["DETAILS"][emp_name] = {
                "prod": item.get('m_prod', 0),
                "scrap": item.get('m_scrap', 0),
                "dlnc": item.get('m_dlnc', 0),
                "reject": item.get('m_reject', 0),
                "screen": item.get('m_screen', 0),
                "visslab": item.get('m_visslab', 0),

                "stop_hr": item.get('m_stop_hr', 0),
                "off_hours": item.get('m_off_hours', 0),
                "mech_hr": item.get('m_mech_hr', 0),
                "order_chg": item.get('m_order_chg', 0),
                "mech_fail": item.get('m_mech_fail', 0),

                "shifts": item.get('m_shifts', 0),
                "runtime": e_runtime,
                "net_hour": e_net_hour,
                "used": e_used,
                "percent_yield": e_percent_yield,
                "oee": e_perfect_time,
                "mttr": e_mttr,
                "perfect_time": e_perfect_time,
            }
        return Response({
            "configs": {
                "summary": [c for c in SUMMARY_CONFIGS if c['chartStatus'] == "Active"],
                "employee": [m for m in METRIC_CONFIGS if m['chartStatus'] == "Active"]
            },
            "data": result
        })
