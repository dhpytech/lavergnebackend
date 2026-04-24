from datetime import datetime, timedelta
from django.db.models import Sum


class BaggingAggregateService:
    @staticmethod
    def get_period_stats(queryset):
        """Hàm helper để tính toán các con số tổng hợp từ một queryset"""
        summary = {"input": 0, "output": 0, "rework": 0}
        for entry in queryset:
            for item in (entry.production_data or []):
                iq = float(item.get('inputQty', 0))
                oq = float(item.get('outputQty', 0))
                if iq == 0:
                    summary["rework"] += oq
                else:
                    summary["input"] += iq
                summary["output"] += oq

        # Tính Yield thực tế
        actual_output = summary["output"] - summary["rework"]
        yield_rate = (actual_output / summary["input"] * 100) if summary["input"] > 0 else 0

        return {
            "input": summary["input"],
            "output": summary["output"],
            "rework": summary["rework"],
            "yield": yield_rate
        }

    @classmethod
    def aggregate_production_data(cls, queryset, filters):
        # 1. Tính toán kỳ hiện tại (Current Period)
        current_stats = cls.get_period_stats(queryset)

        # 2. Lấy dữ liệu đối soát (Last Month & Last Year)
        # Giả sử filters['start_date'] là string 'YYYY-MM-DD'
        start_dt = datetime.strptime(filters['start_date'], '%Y-%m-%d')
        end_dt = datetime.strptime(filters['end_date'], '%Y-%m-%d')
        delta = end_dt - start_dt

        # Last Month (Cùng khoảng thời gian nhưng lùi 1 tháng)
        lm_start = (start_dt - timedelta(days=30))
        lm_end = (end_dt - timedelta(days=30))

        # Last Year (Cùng khoảng thời gian nhưng lùi 1 năm)
        ly_start = start_dt.replace(year=start_dt.year - 1)
        ly_end = end_dt.replace(year=end_dt.year - 1)

        # Truy vấn dữ liệu quá khứ (Sử dụng Selector để lấy queryset tương ứng)
        # Lưu ý: Cần import selector ở đầu file hoặc gọi trực tiếp Model
        from ..models import BaggingInput
        lm_qs = BaggingInput.objects.filter(date__range=[lm_start, lm_end])
        ly_qs = BaggingInput.objects.filter(date__range=[ly_start, ly_end])

        lm_stats = cls.get_period_stats(lm_qs)
        ly_stats = cls.get_period_stats(ly_qs)

        # 3. Chuẩn bị dữ liệu cho Charts (Dựa trên queryset hiện tại)
        daily_series = {}
        product_mix = {}
        lot_data = {}

        for entry in queryset:
            date_key = entry.date.strftime("%d/%m")
            lot_no = entry.lot_number or "N/A"
            if lot_no not in lot_data:
                lot_data[lot_no] = {"input": 0, "output": 0, "rework": 0, "reject": 0}
            if date_key not in daily_series:
                daily_series[date_key] = 0

            for item in (entry.production_data or []):
                iq = float(item.get('inputQty', 0))
                oq = float(item.get('outputQty', 0))
                p_code = item.get('productCode', 'Other')

                daily_series[date_key] += oq
                product_mix[p_code] = product_mix.get(p_code, 0) + oq

                if iq != 0:
                    lot_data[lot_no]["input"] += iq
                    lot_data[lot_no]["reject"] += (iq - oq)
                else:
                    lot_data[lot_no]["rework"] += oq
                lot_data[lot_no]["output"] += oq

        # 4. Trả về cấu trúc khớp 100% với StatCard của Maris
        return {
            "kpis": {
                "Total Input (KG)": {
                    "value": f"{current_stats['input']:,.0f}",
                    "lastMonth": lm_stats['input'],
                    "lastYear": ly_stats['input']
                },
                "Total Output (KG)": {
                    "value": f"{current_stats['output']:,.0f}",
                    "lastMonth": lm_stats['output'],
                    "lastYear": ly_stats['output']
                },
                "Rework Qty (KG)": {
                    "value": f"{current_stats['rework']:,.0f}",
                    "lastMonth": lm_stats['rework'],
                    "lastYear": ly_stats['rework']
                },
                "Yield Rate (%)": {
                    "value": f"{current_stats['yield']:.2f}%",
                    "lastMonth": lm_stats['yield'],
                    "lastYear": ly_stats['yield']
                }
            },
            "charts": {
                "column_chart": [{"name": k, "volume": v} for k, v in product_mix.items()],
                "pie_chart": [{"name": k, "value": v} for k, v in product_mix.items()]
            },
            "lots": [{"lot": k, **v} for k, v in lot_data.items()]
        }
