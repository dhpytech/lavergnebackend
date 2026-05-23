# entries/services.py
from datetime import datetime
from dashboards.queries.maris_query import MarisQuery, FetchParams
from dashboards.services.statistics import ProductionStats
from dashboards.services.aggregators import ProductionAggregator


class MarisIsoReportService:
    @staticmethod
    def _crunch_for_shift(target_date, shift_name, query_product_code):
        p = FetchParams(start=target_date, end=target_date, shift=shift_name,
                        product_code=query_product_code or "total")
        qs = MarisQuery.fetch_records(p)
        normalized = ProductionAggregator.normalize(qs)

        dummy_safety = {"incident": 0, "accident": 0}
        stats = ProductionStats(normalized, [], [], dummy_safety, dummy_safety, dummy_safety)

        # 1. Lấy toàn bộ kết quả trả về từ hàm tính toán gốc của bạn
        raw_calculated = stats.calculate()

        # 2. Tách phần map dlnc_case ra (nếu dlnc_cases được xử lý trong stats)
        # Nếu hàm _get_raw chưa map dlnc_case, ta xử lý nhanh tại đây:
        dlnc_cases_map = {}
        stop_details = []
        problem_details = []

        for d in normalized:
            case_name = d.get("dlnc_case", "None")
            if d.get("dlnc", 0) > 0 and case_name.lower() != "none":
                dlnc_cases_map[case_name] = dlnc_cases_map.get(case_name, 0.0) + d["dlnc"]

            if d.get("stopTimes"):
                stop_details.extend(d["stopTimes"])
            if d.get("problems"):
                problem_details.extend(d["problems"])

        # Trả về một dictionary bọc gọn gàng
        return {
            "kpis": raw_calculated,  # Đút toàn bộ bảng KPIs cũ vào đây
            "dlnc_cases_breakdown": dlnc_cases_map,
            "raw_normalized_list": normalized,
            "stop_details_list": stop_details,
            "problem_details_list": problem_details
        }

    @classmethod
    def generate_full_report(cls, date_str, product_code=None):
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        day_shift_res = cls._crunch_for_shift(target_date, "day", product_code)
        night_shift_res = cls._crunch_for_shift(target_date, "night", product_code)
        total_res = cls._crunch_for_shift(target_date, "total", product_code)

        # Bây giờ các key "kpis", "dlnc_cases_breakdown",... đã tồn tại an toàn tuyệt đối
        return {
            "date": date_str,
            "day_shift": day_shift_res["kpis"],
            "night_shift": night_shift_res["kpis"],
            "total": total_res["kpis"],

            "dlnc_breakdown": {
                "day": day_shift_res["dlnc_cases_breakdown"],
                "night": night_shift_res["dlnc_cases_breakdown"],
                "total": total_res["dlnc_cases_breakdown"]
            },

            "raw_production_details": total_res["raw_normalized_list"],
            "raw_stop_details": total_res["stop_details_list"],
            "raw_problem_details": total_res["problem_details_list"]
        }
