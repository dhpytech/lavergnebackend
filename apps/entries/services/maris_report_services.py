# entries/services.py
from datetime import datetime
from dashboards.queries.maris_query import MarisQuery, FetchParams
from dashboards.services.statistics import ProductionStats
from dashboards.services.aggregators import ProductionAggregator


class MarisIsoReportService:
    @staticmethod
    def _crunch_for_shift(target_date, shift_name, query_product_code="total"):
        p = FetchParams(
            start=target_date,
            end=target_date,
            shift=shift_name,
            product_code=query_product_code
        )
        qs = MarisQuery.fetch_records(p)
        normalized = ProductionAggregator.normalize(qs)
        dummy_safety = {"incident": 0, "accident": 0}

        employees_set = set()
        product_codes_set = set()

        for item in normalized:
            emp = item.get("employee")
            if emp and str(emp).strip():
                employees_set.add(str(emp).strip())

            p_code = item.get("productCode")
            if p_code and str(p_code).strip():
                product_codes_set.add(str(p_code).strip())

        stats = ProductionStats(normalized, [], [], dummy_safety, dummy_safety, dummy_safety)
        raw_calculated = stats._get_raw(stats.data, stats.safety)

        yield_pct = raw_calculated["yield_pct"]
        used_pct = raw_calculated["used_pct"]
        rated_pct = raw_calculated["rate"]
        lost_disp = raw_calculated["stop_hr_no_weekend"]*raw_calculated["net_hr"]

        oee = yield_pct * used_pct * rated_pct
        visslabPercent = raw_calculated["visslab"]/raw_calculated["total_output"] if raw_calculated["total_output"] else 0
        setting_kgh = raw_calculated["total_output"]/raw_calculated["perfect_time"] if raw_calculated["perfect_time"] else 0,
        metrics_summary = {
            "prod": raw_calculated["prod"],
            "goodPro": raw_calculated["goodPro"],
            "dlnc": raw_calculated["dlnc"],
            "scrap": raw_calculated["scrap"],
            "scrapDie": raw_calculated["scrapDie"],
            "screen": raw_calculated["screen"],
            "visslab": raw_calculated["visslab"],
            "output": raw_calculated["total_all_output"],
            "visslabPercent": visslabPercent,
            "stop_hr": raw_calculated["stop_hr"],
            "stop_hr_no_weekend": raw_calculated["stop_hr_no_weekend"],
            "off_hours": raw_calculated["off_hours"],
            "oee_pct": oee,
            "yield_pct": raw_calculated["yield_pct"],
            "used_pct": raw_calculated["used_pct"],
            "rate": rated_pct,
            "perfect_time": raw_calculated["perfect_time"],
            "net_hr": raw_calculated["net_hr"],
            "comments": raw_calculated["comments"],
            "lost_disp": lost_disp,
            "setting_kgh":setting_kgh,

            "employees": ", ".join(sorted(list(employees_set))) if employees_set else "-",
            "product_codes": ", ".join(sorted(list(product_codes_set))) if product_codes_set else "-",
        }

        return {
            "metrics": metrics_summary,
            "dlnc_cases": raw_calculated["dlnc_cases"],
            "normalized_list": normalized,
            "stop_details_list": raw_calculated["stop_details_list"],
            "problem_details_list": raw_calculated["problem_details_list"]
        }

    @classmethod
    def generate_daily_report(cls, date_str, product_code="total"):
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        day_res = cls._crunch_for_shift(target_date, "day", product_code)
        night_res = cls._crunch_for_shift(target_date, "night", product_code)
        total_res = cls._crunch_for_shift(target_date, "total", product_code)

        return {
            "success": True,
            "data": {
                "date": date_str,
                "product_code": product_code,

                "kpis": {
                    "day": day_res["metrics"],
                    "night": night_res["metrics"],
                    "total": total_res["metrics"]
                },

                "dlnc_breakdown": {
                    "day": day_res["dlnc_cases"],
                    "night": night_res["dlnc_cases"],
                    "total": total_res["dlnc_cases"]
                },

                "stop_details": {
                    "day": day_res["stop_details_list"],
                    "night": night_res["stop_details_list"],
                    "total": total_res["stop_details_list"]
                },

                "problem_details": {
                    "day": day_res["problem_details_list"],
                    "night": night_res["problem_details_list"],
                    "total": total_res["problem_details_list"]
                },

                "raw_problem_details": total_res["problem_details_list"]
            }
        }
