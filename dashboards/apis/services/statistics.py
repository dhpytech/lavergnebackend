import datetime
from utilities.number_format import format_number


class ProductionStats:
    # dlnc: int
    # SHIFT_HOURS = 24  # full day default
    def __init__(self, records, start_date, end_date, model_cls):
        """
        records: list of dict (có thể là JSONField trong DB)
        model_cls: model để query so sánh
        """
        self.records = records or []
        self.start_date = start_date
        self.end_date = end_date
        self.model_cls = model_cls

        # tổng hợp
        self.production = 0
        self.scrap = 0
        self.dlnc = 0
        self.reject = 0
        self.screen = 0
        self.visslab = 0
        self.stop_time = 0
        self.order_change = 0
        self.mech_fail = 0
        self.repair_time = 0
        self.shift_time = 0
        self.num_records = len(records)
        self.stop_count = 0
        self.off_days = 0
        self.mechanical_time = 0
        self.rate = 0
    # ==================== Tính toán hiện tại ====================
    def calculate(self):
        """Tính toán chỉ số cho khoảng thời gian hiện tại"""

        for rec in self.records:
            rec_dict = dict(rec) if isinstance(rec, dict) else getattr(rec, "__dict__", {})

            main_data = rec_dict.get("mainData") or []
            stop_times = rec_dict.get("stopTimes") or []

            for item in main_data:
                self.production += int(item.get("goodPro", 0) or 0) + int(item.get("dlnc", 0) or 0)
                self.scrap += int(item.get("scrap", 0) or 0)
                self.dlnc += int(item.get("dlnc", 0) or 0)
                self.reject += int(item.get("reject", 0) or 0)
                self.screen += int(item.get("screen", 0) or 0)
                self.visslab += int(item.get("visslab", 0) or 0)

                # self.rate += int(item.get("rate", 0) or 0)
            for stop in stop_times:
                self.stop_count += 1
                self.stop_time += float(stop.get("hour", 0) or 0)
                if stop.get("stopTime") == "# ORDER CHANGE":
                    self.order_change += 1
                elif stop.get("stopTime") == "# OF MECHANICAL FAILURE":
                    self.mech_fail += 1
                elif stop.get("stopTime") == "MECHANICAL/ELECTRICAL FAILURE":
                    self.mechanical_time += float(stop.get("hour", 0) or 0)
                else:
                    self.repair_time += float(stop.get("hour", 0) or 0)

                if stop.get("stopTime") == "HOLIDAY" or stop.get("stopTime") == "WEEKEND OFF":
                    self.off_days += 1
        return self._format_result()

    def _format_result(self):
        self.shift_time = (self.num_records-self.off_days) * 12
        used_percent = (self.shift_time - self.repair_time) / self.shift_time if self.shift_time > 0 else 0
        yield_percent = (
            self.production/(self.production + self.reject + self.scrap + self.screen)
            if (self.production + self.reject + self.scrap + self.screen) > 0
            else 0
        )
        net_hour = ((self.production + self.reject + self.scrap + self.screen + self.visslab) /
                    (self.shift_time - self.repair_time) if (self.shift_time - self.repair_time) > 0 else 0)

        scrap_production = round(((self.scrap+self.screen)/self.production) * 100 if self.production > 0 else 0, 2)

        mttr = self.mechanical_time/self.mech_fail if self.mech_fail > 0 else 0
        mtbf = self.shift_time / self.mech_fail if self.mech_fail > 0 else self.shift_time

        # Tinh Toán Rate Theo Bình Quân Ngày
        oee = used_percent * yield_percent # Nhân thêm cho Rate

        return {
            "PRODUCTION (KG)": self.production,
            "SCRAP (KG)": self.scrap + self.screen,
            "DL/NC (KG)": self.dlnc,
            "SCRAP/PRODUCTION (%)": format_number(scrap_production),
            "STOP TIME (HOUR)": self.repair_time,
            "NUMBER OF ORDER CHANGE": self.order_change,
            "NUMBER OF MECHANICAL FAILURE": self.mech_fail,
            "NET/HOUR (KG/HOUR)": round(net_hour, 3),
            "UTILISATION (%)": f"{used_percent:.2%}",
            "YIELD (%)": f"{yield_percent:.2%}",
            "OEE (%)": f"{oee:.2%}",
            "MTTR (HOUR)": round(mttr, 2),
            "MTBF (HOUR)": round(mtbf, 2),
        }

    # ==================== So sánh ====================
    def compare_with_previous(self):
        """Tính % thay đổi với tháng trước và năm trước"""
        last_month_start = (self.start_date - datetime.timedelta(days=30))
        last_month_end = self.start_date - datetime.timedelta(days=1)

        last_year_start = self.start_date.replace(year=self.start_date.year - 1)
        last_year_end = self.end_date.replace(year=self.end_date.year - 1)

        # Query dữ liệu
        last_month_qs = self.model_cls.objects.filter(date__range=[last_month_start, last_month_end])
        last_year_qs = self.model_cls.objects.filter(date__range=[last_year_start, last_year_end])

        # Ép sang dict sạch (chỉ lấy field JSON nếu có)
        def to_dict_list(qs):
            return [getattr(r, "data", r.__dict__) for r in qs]

        last_month_stats = ProductionStats(to_dict_list(last_month_qs), last_month_start, last_month_end, self.model_cls).calculate()
        last_year_stats = ProductionStats(to_dict_list(last_year_qs), last_year_start, last_year_end, self.model_cls).calculate()

        current_stats = self.calculate()
        return self._add_comparison(current_stats, last_month_stats, last_year_stats)

    def _add_comparison(self, current, last_month, last_year):
        def calc_change(cur, prev):
            if prev == 0:
                return 0
            return round(((cur - prev) / prev) * 100, 2)

        result = {}
        for key, cur_val in current.items():
            if isinstance(cur_val, (int, float)):
                lm_val = last_month.get(key, 0)
                ly_val = last_year.get(key, 0)
                result[key] = {
                    "value": cur_val,
                    "lastMonth": f"{calc_change(cur_val, lm_val)}%",
                    "lastYear": f"{calc_change(cur_val, ly_val)}%",
                }
            else:
                result[key] = {"value": cur_val, "lastMonth": "0%", "lastYear": "0%"}
        return result
