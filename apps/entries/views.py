from rest_framework import viewsets
from .models import MarisInput, MetalInput, BaggingInput
from .serializers import MarisInputSerializer, MetalInputSerializer, BaggingInputSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MarisInputFilter
import calendar
from django.utils import timezone
from rest_framework.response import Response
from collections import defaultdict


# 1. Maris ViewSet
class MarisInputViewSet(viewsets.ModelViewSet):
    queryset = MarisInput.objects.all()
    serializer_class = MarisInputSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MarisInputFilter

    # filterset_fields = {
    #     'date': ['gte', 'lte'],
    # }


# 2. Metal ViewSet
class MetalInputViewSet(viewsets.ModelViewSet):
    queryset = MetalInput.objects.all()
    serializer_class = MetalInputSerializer


# 3. Bagging ViewSet
class BaggingInputViewSet(viewsets.ModelViewSet):
    queryset = BaggingInput.objects.all()
    serializer_class = BaggingInputSerializer


class IsoMonthlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MarisInput.objects.all().order_by('date')
    serializer_class = MarisInputSerializer
    filterset_class = MarisInputFilter

    def list(self, request, *args, **kwargs):
        shift_param = request.query_params.get('shift', 'total').lower()
        default_shift_time = 24 if shift_param == 'total' else 12

        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = int(request.query_params.get('year', timezone.now().year))
        except ValueError:
            return Response({"error": "Invalid month/year"}, status=400)

        _, last_day = calendar.monthrange(year, month)

        # 1. Lấy dữ liệu qua Filter
        query_params = request.query_params.copy()
        query_params.update({'start': f"{year}-{month:02d}-01", 'end': f"{year}-{month:02d}-{last_day}"})
        filtered_qs = MarisInputFilter(query_params, queryset=self.get_queryset()).qs

        # 2. Khởi tạo Ma trận (Index 0 = Ngày 1)
        matrix = {
            'summary': {
                "production_total": [0.0] * last_day,
                "scrap_total": [0.0] * last_day,
                "stop_time_total": [0.0] * last_day,
                "shift_time": [float(default_shift_time)] * last_day,
                "net_hour": [0.00] * last_day,
                "percent_used": [0.00] * last_day,
                "percent_yield": [0.00] * last_day,
                "MTTR": [0.00] * last_day,
                "MTBF": [0.00] * last_day,
            },
            "production": defaultdict(lambda: [0] * last_day),
            "reject": defaultdict(lambda: [0] * last_day),
            "scrap": defaultdict(lambda: [0] * last_day),
            "screen": defaultdict(lambda: [0] * last_day),
            "visslab": defaultdict(lambda: [0] * last_day),
            "dlnc": defaultdict(lambda: [0] * last_day),
            "downtime": defaultdict(lambda: [0] * last_day),
            "numtime": defaultdict(lambda: [0] * last_day),
            "problems": defaultdict(lambda: [0] * last_day),
            "operators": defaultdict(lambda: [[] for _ in range(last_day)])
        }

        KEY_HOURS = "MECHANICAL/ELECTRICAL FAILURE"
        KEY_TIMES = "# OF MECHANICAL FAILURE"
        ORDER_TIMES = "# ORDER CHANGE"

        # 3. Flatten dữ liệu
        for rec in filtered_qs:
            day_idx = rec.date.day - 1

            # Operator
            emp_name = str(rec.employee).strip() if rec.employee else ""
            if emp_name:
                if emp_name not in matrix["operators"]["operator"][day_idx]:
                    matrix["operators"]["operator"][day_idx].append(emp_name)

            # Production & Scrap
            for p in rec.production_data:
                sku = p.get('productCode', 'N/A')
                matrix["production"][sku][day_idx] += float(p.get('goodPro', 0))
                matrix["reject"][sku][day_idx] += float(p.get('reject', 0))
                matrix["scrap"][sku][day_idx] += float(p.get('scrap', 0))
                matrix["screen"][sku][day_idx] += float(p.get('screen', 0))
                matrix["visslab"][sku][day_idx] += float(p.get('visslab', 0))
                matrix["dlnc"][sku][day_idx] += float(p.get('dlnc', 0))

                matrix["summary"]["production_total"][day_idx] += float(p.get('goodPro', 0)) + float(p.get('dlnc', 0))
                matrix["summary"]["scrap_total"][day_idx] += (float(p.get('reject', 0)) + float(p.get('scrap', 0)) +
                                                              float(p.get('screen', 0)))

            # Stop Time (Downtime)
            for stop in getattr(rec, 'stop_time_data', []):

                REASON_KEYS = [KEY_TIMES, ORDER_TIMES]
                reason = stop.get('stopTime', 'Others')

                if reason not in REASON_KEYS:
                    matrix["downtime"][reason][day_idx] += float(stop.get('hour', 0) or 0)
                    matrix["summary"]["stop_time_total"][day_idx] += float(stop.get('hour', 0) or 0)
                else:
                    matrix["numtime"][reason][day_idx] += float(stop.get('hour', 0) or 0)

                if (matrix["summary"]["stop_time_total"][day_idx] == matrix["summary"]["shift_time"][day_idx]
                        and matrix["summary"]["shift_time"][day_idx] != 0):
                    matrix["summary"]["stop_time_total"][day_idx] = len(matrix["operators"]["operator"][day_idx])*12
                    matrix["summary"]["shift_time"][day_idx] = len(matrix["operators"]["operator"][day_idx])*12

            # Problems
            for prob in getattr(rec, 'problem_data', []):
                p_type = prob.get('problem', 'Others')
                matrix["problems"][p_type][day_idx] += float(prob.get('hour', 0) or 0)

        for key in matrix["operators"]:
            for day_idx in range(last_day):
                names_list = matrix["operators"][key][day_idx]
                # Chuyển từ mảng [P1, P2] thành chuỗi "P1 - P2"
                matrix["operators"][key][day_idx] = " - ".join(names_list) if names_list else ""

        mech_times_total = 0
        mech_hours_total = 0
        for i in range(last_day):

            p_total = matrix["summary"]["production_total"][i]
            w_total = matrix["summary"]["scrap_total"][i]
            s_total = matrix["summary"]["stop_time_total"][i]
            sh_time = matrix["summary"]["shift_time"][i]

            day_mech_hours = matrix["downtime"].get(KEY_HOURS, [0] * last_day)[i]
            day_mech_times = matrix["numtime"].get(KEY_TIMES, [0] * last_day)[i]

            # Cộng dồn cho tổng cả tháng
            mech_hours_total += day_mech_hours
            mech_times_total += day_mech_times

            # Net/Hour = Sản lượng / (Thời gian chạy thực tế)
            run_time = sh_time - s_total
            if run_time > 0:
                matrix["summary"]["net_hour"][i] = round((p_total + w_total) / run_time, 2)
                matrix["summary"]["percent_used"][i] = round((run_time / sh_time) * 100, 2)

            # % Yield = Sản lượng / (Sản lượng + Phế phẩm)
            if (p_total + w_total) > 0:
                matrix["summary"]["percent_yield"][i] = round((p_total / (p_total + w_total)) * 100, 2)

        summary = matrix["summary"]

        # Tính các giá trị Tổng thô (SUM)
        t_prod = sum(summary["production_total"])
        t_waste = sum(summary["scrap_total"])
        t_stop = sum(summary["stop_time_total"])
        t_shift = sum(summary["shift_time"])

        # Tính toán các chỉ số Hiệu suất theo tháng (Weighted Average)
        # Không dùng sum() các cột % vì sẽ ra con số hàng nghìn % sai lệch
        t_run_time = t_shift - t_stop

        final_mttr = round(mech_hours_total / mech_times_total, 2) if mech_times_total > 0 else 0
        final_mtbf = round(t_run_time / mech_times_total, 2) if mech_times_total > 0 else 0

        print(mech_times_total)
        grand_totals = {
            "production_total": t_prod,
            "scrap_total": t_waste,
            "stop_time_total": t_stop,
            "shift_time": t_shift,
            "net_hour": round((t_prod + t_waste) / t_run_time, 2) if t_run_time > 0 else 0,
            "percent_used": round((t_run_time / t_shift) * 100, 2) if t_shift > 0 else 0,
            "percent_yield": round((t_prod / (t_prod + t_waste)) * 100, 2) if (t_prod + t_waste) > 0 else 0,
            "MTTR": final_mttr,
            "MTBF": final_mtbf,
        }

        return Response({
            "metadata": {"month": month, "year": year, "last_day": last_day},
            "matrix": matrix,
            "summary_totals": grand_totals
        })
