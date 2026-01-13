from django.db.models import Sum


class ChartGenerator:
    @staticmethod
    def generate(qs):
        production_data = []

        for obj in qs:
            for item in (obj.production_data or []):
                production_data.append({
                    "productCode": item.get("productCode"),
                    "production": int(item.get("goodPro", 0)) + int(item.get("dlnc", 0))
                })

        aggregated = {}
        for row in production_data:
            code = row["productCode"]
            if not code:
                continue
            aggregated[code] = aggregated.get(code, 0) + row["production"]

        total = sum(aggregated.values()) or 1

        chart_data = [
            {
                "name": k,
                "value": v,
                "percent": round(v / total, 2)
            }
            for k, v in aggregated.items()
        ]
        chart_data.sort(key=lambda x: -x["value"])

        return {
            "production_pie": chart_data,
            "production_bar": chart_data,
        }
