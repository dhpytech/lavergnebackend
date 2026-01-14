# dashboards/services/charts.py

class ChartGenerator:
    @staticmethod
    def by_product(normalized_data):
        """Tạo dữ liệu cho biểu đồ tròn (Pie Chart) hoặc cột (Bar Chart) theo sản phẩm"""
        aggregated = {}
        for d in normalized_data:
            code = d["productCode"]
            if not code: continue
            # Tổng hợp Sản lượng = Good + DLNC
            aggregated[code] = aggregated.get(code, 0) + d["goodPro"] + d["dlnc"]

        # Format lại cho Frontend (Recharts)
        return [
            {"name": k, "value": v}
            for k, v in sorted(aggregated.items(), key=lambda x: -x[1])
        ]

    @staticmethod
    def by_date(normalized_data):
        """Tạo dữ liệu cho biểu đồ đường (Line Chart) theo tiến độ thời gian"""
        daily = {}
        for d in normalized_data:
            date_str = d["date"].strftime("%d/%m")
            daily[date_str] = daily.get(date_str, 0) + d["goodPro"]

        return [
            {"date": k, "production": v}
            for k, v in daily.items()
        ]
