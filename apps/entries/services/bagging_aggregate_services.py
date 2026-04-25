# apps/entries/services/bagging_aggregate_services.py
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BaggingAggregateService:
    def _diff(self, curr, past):
        if not past or past == 0: return "+0.0%"
        diff = ((curr - past) / past) * 100
        return f"{diff:+.1f}%"

    def get_raw_metrics(self, queryset):
        res = {"in": 0, "ship": 0, "rw": 0, "time": 0}
        try:
            for entry in queryset:
                # Giả định mỗi entry tính là 8h nếu không có data cụ thể
                res["time"] += 12

                prod_data = entry.production_data or []
                if not isinstance(prod_data, list): continue

                for item in prod_data:
                    # Dùng float(item.get(..., 0) or 0) để tránh null
                    iq = float(item.get('inputQty') or 0)
                    oq = float(item.get('outputQty') or 0)

                    if iq == 0:
                        res["rw"] += oq
                    else:
                        res["in"] += iq
                    res["ship"] += oq
        except Exception as e:
            logger.error(f"Error in get_raw_metrics: {e}")

        res["rate"] = (res["ship"] / res["in"] * 100) if res["in"] > 0 else 0
        return res

    @classmethod
    def aggregate_production_data(cls, queryset, filters):
        inst = cls()
        curr = inst.get_raw_metrics(queryset)

        # Xử lý ngày tháng an toàn
        try:
            s_dt = datetime.strptime(filters.get('start', '2026-01-01'), '%Y-%m-%d')
            e_dt = datetime.strptime(filters.get('end', '2026-01-01'), '%Y-%m-%d')
        except:
            s_dt = e_dt = datetime.now()

        # Query dữ liệu so sánh
        from ..models import BaggingInput
        lm_qs = BaggingInput.objects.filter(date__range=[s_dt - timedelta(days=30), e_dt - timedelta(days=30)])
        ly_qs = BaggingInput.objects.filter(
            date__range=[s_dt.replace(year=s_dt.year - 1), e_dt.replace(year=e_dt.year - 1)])

        lm = inst.get_raw_metrics(lm_qs)
        ly = inst.get_raw_metrics(ly_qs)

        # Gom dữ liệu Chart & Table
        daily_series = {}
        product_mix = {}
        lot_summary = {}

        for entry in queryset:
            d_key = entry.date.strftime("%d/%m")
            l_no = entry.lot_number or "N/A"

            if l_no not in lot_summary:
                lot_summary[l_no] = {"lot": l_no, "in": 0, "out": 0, "rw": 0, "rj": 0, }

            for item in (entry.production_data or []):
                iq = float(item.get('inputQty') or 0)
                oq = float(item.get('outputQty') or 0)
                p_code = item.get('productCode', 'Other')

                daily_series[d_key] = daily_series.get(d_key, 0) + oq
                product_mix[p_code] = product_mix.get(p_code, 0) + oq

                if iq == 0:
                    lot_summary[l_no]["rw"] += oq
                else:
                    lot_summary[l_no]["in"] += iq
                lot_summary[l_no]["out"] += oq
            lot_summary[l_no]["rj"] = lot_summary[l_no]["in"] - lot_summary[l_no]["out"]

        lot_chart_final = []
        for l_no, stats in lot_summary.items():
            lot_chart_final.append({
                "name": l_no,
                "input": stats["in"],
                "shipping": stats["out"],
                "reject": stats["rj"]
            })
        return {
            "kpis": {
                "TOTAL IN": {
                    "value": f"{curr['in']:,.0f}",
                    "lastMonth": inst._diff(curr['in'], lm['in']),
                    "lastYear": inst._diff(curr['in'], ly['in'])
                },
                "SHIPPING": {
                    "value": f"{curr['ship']:,.0f}",
                    "lastMonth": inst._diff(curr['ship'], lm['ship']),
                    "lastYear": inst._diff(curr['ship'], ly['ship'])
                },
                "RATE": {
                    "value": f"{curr['rate']:.1f}%",
                    "lastMonth": inst._diff(curr['rate'], lm['rate']),
                    "lastYear": inst._diff(curr['rate'], ly['rate'])
                },
                "WORKING TIME": {
                    "value": f"{curr['time']:,.0f}h",
                    "lastMonth": inst._diff(curr['time'], lm['time']),
                    "lastYear": inst._diff(curr['time'], ly['time'])
                }
            },
            "charts": {
                "bar_chart": [{"name": k, "volume": v} for k, v in product_mix.items()],
                "pie_chart": [{"name": k, "value": v} for k, v in product_mix.items()],
                "lot_chart": lot_chart_final
            },
            "lots": sorted(lot_summary.values(), key=lambda x: x['lot'], reverse=True)
        }
