from collections import defaultdict


class ChartService:
    @staticmethod
    def get_production_charts(records):
        product_map = defaultdict(float)
        daily_map = defaultdict(float)

        for r in records:
            # Logic: Value = GoodPro + DLNC
            val = float(r.get("goodPro") or 0) + float(r.get("dlnc") or 0)
            p_code = r.get("productCode", "N/A")
            date_str = r.get("date")

            product_map[p_code] += val
            daily_map[date_str] += val

        total_all = sum(product_map.values())

        # Pie Chart: Trả về phần trăm (%)
        pie_data = [
            {
                "name": k,
                "value": round((v / total_all * 100), 2) if total_all > 0 else 0
            }
            for k, v in product_map.items()
        ]

        # Column Chart: Trả về giá trị thực tế (KG)
        column_data = [
            {"name": k, "volume": round(v, 2)}
            for k, v in sorted(product_map.items())
        ]

        return {
            "pie_chart": pie_data,
            "column_chart": column_data
        }
