# dashboards/apis/services/charts.py
from django.db.models import Sum


class ChartGenerator:
    @staticmethod
    def generate(qs):
        # tổng production per productCode
        production_data = []
        for obj in qs:
            for item in obj.mainData:
                production_data.append({
                    "productCode": item.get("productCode"),
                    "production": int(item.get("goodPro", 0)) + int(item.get("dlnc", 0))
                })

        # gom nhóm
        aggregated = {}
        for row in production_data:
            code = row["productCode"]
            aggregated[code] = aggregated.get(code, 0) + row["production"]

        chart_data = [{"productCode": k, "production": v} for k, v in aggregated.items()]
        chart_data.sort(key=lambda x: -x["production"])

        return {
            "production_pie": chart_data,  # Pie chart
            "production_bar": chart_data,  # Bar chart
        }
