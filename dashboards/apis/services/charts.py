# dashboards/apis/services/charts.py
from django.db.models import Sum


class ChartGenerator:
    @staticmethod
    def generate(qs):
        # Tổng hợp production per productCode
        production_data = []
        for obj in qs:
            for item in obj.mainData:
                production_data.append({
                    "productCode": item.get("productCode"),
                    "production": int(item.get("goodPro", 0)) + int(item.get("dlnc", 0))
                })

        # Tổng hợp theo product code
        aggregated = {}
        for row in production_data:
            code = row["productCode"]
            aggregated[code] = aggregated.get(code, 0) + row["production"]

        total = sum(aggregated.values()) or 1  # tránh chia 0

        # Format dữ liệu chuẩn Recharts
        chart_data = [
            {
                "name": k,                         # Recharts dùng name
                "value": v,                        # Recharts dùng value
                "percent": round(v / total, 2)  # phần trăm hiển thị
            }
            for k, v in aggregated.items()
        ]
        chart_data.sort(key=lambda x: -x["value"])

        return {
            "production_pie": chart_data,  # Dữ liệu cho PieChart
            "production_bar": chart_data,  # Dữ liệu cho BarChart
        }
