from datetime import datetime
from entries.models import MarisInput
from dashboards.queries.maris_query import MarisQuery, FetchParams
from dashboards.services.statistics import ProductionStats
from dashboards.services.aggregators import ProductionAggregator


class MarisIsoReportService:
    @staticmethod
    def _get_stats_for_shift(target_date, shift_value, product_code="total"):
        p_current = FetchParams(
            start=target_date,
            end=target_date,
            shift=shift_value,
            # product_code=product_code if product_code else "total"
        )
        qs_current = MarisQuery.fetch_records(p_current)
        current_data = ProductionAggregator.normalize(qs_current)
        empty_list = []
        safety_dummy = {"incident": 0, "accident": 0}

        stats_calculator = ProductionStats(
            current_data=current_data,
            lm_data=empty_list,
            ly_data=empty_list,
            safety_curr=safety_dummy,
            safety_lm=safety_dummy,
            safety_ly=safety_dummy
        )

        raw_calculated = stats_calculator.calculate()

        # 6. Trích xuất mã sản phẩm từ tập data đã normalize để đưa lên bảng ISO
        codes = sorted(list(set([item.get("productCode") for item in current_data if item.get("productCode")])))

        # Gom kết quả chỉ lấy trường "value" thực tế của ngày hôm đó
        shift_metrics = {
            "product_codes": codes,
        }
        for kpi_name, kpi_data in raw_calculated.items():
            shift_metrics[kpi_name] = kpi_data["value"]

        return shift_metrics

    @classmethod
    def generate_iso_report(cls, target_date_str, product_code=None):
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()

        return {
            "date": target_date_str,
            "day_shift": cls._get_stats_for_shift(target_date, "day", product_code),
            "night_shift": cls._get_stats_for_shift(target_date, "night", product_code),
            "total": cls._get_stats_for_shift(target_date, "total", product_code)
        }