from utils.number_format import format_number


class ProductionStats:
    def __init__(self, normalized_data, start_date, end_date):
        self.data = normalized_data
        self.start_date = start_date
        self.end_date = end_date

    def calculate(self):
        p = {
            "prod": 0, "scrap": 0, "dlnc": 0, "reject": 0, "visslab": 0,
            "stop_hr": 0, "order_chg": 0, "mech_fail": 0, "mech_hr": 0, "off_days": 0
        }

        for d in self.data:
            p["prod"] += d["goodPro"] + d["dlnc"]
            p["scrap"] += d["scrap"]
            p["dlnc"] += d["dlnc"]
            p["reject"] += d["reject"]
            p["visslab"] += d["visslab"]

            for s in d["stopTimes"]:
                hr = float(s.get("hour") or 0)
                st = s.get("stopTime", "")
                if st in ["HOLIDAY", "WEEKEND OFF"]:
                    p["off_days"] += 1
                elif st == "# ORDER CHANGE":
                    p["order_chg"] += 1
                elif st == "# OF MECHANICAL FAILURE":
                    p["mech_fail"] += 1
                elif st == "MECHANICAL/ELECTRICAL FAILURE":
                    p["mech_hr"] += hr
                    p["stop_hr"] += hr
                else:
                    p["stop_hr"] += hr

        # Tính toán tỷ lệ
        num_shifts = len(set((d["date"], d["shift"]) for d in self.data))
        total_hr = (num_shifts - p["off_days"]) * 12

        used_pct = (total_hr - p["stop_hr"]) / total_hr if total_hr > 0 else 0
        yield_pct = p["prod"] / (p["prod"] + p["reject"] + p["scrap"]) if (p["prod"] + p["reject"] + p[
            "scrap"]) > 0 else 0
        net_hr = (p["prod"] + p["reject"] + p["scrap"] + p["visslab"]) / (total_hr - p["stop_hr"]) if (total_hr - p[
            "stop_hr"]) > 0 else 0

        return {
            "PRODUCTION (KG)": p["prod"],
            "SCRAP (KG)": p["scrap"],
            "DL/NC (KG)": p["dlnc"],
            "SCRAP/PRODUCTION (%)": round((p["scrap"] / p["prod"]) * 100, 2) if p["prod"] > 0 else 0,
            "STOP TIME (HOUR)": round(p["stop_hr"], 2),
            "NUMBER OF ORDER CHANGE": p["order_chg"],
            "NUMBER OF MECHANICAL FAILURE": p["mech_fail"],
            "NET/HOUR (KG/HOUR)": round(net_hr, 2),
            "UTILISATION (%)": f"{used_pct:.2%}",
            "YIELD (%)": f"{yield_pct:.2%}",
            "OEE (%)": f"{(used_pct * yield_pct):.2%}",
            "MTTR (HOUR)": round(p["mech_hr"] / p["mech_fail"], 2) if p["mech_fail"] > 0 else 0,
            "MTBF (HOUR)": round(total_hr / p["mech_fail"], 2) if p["mech_fail"] > 0 else total_hr,
            "INCIDENT (TIMES)": 0,  # Sẽ lấy từ SafetyQuery
            "ACCIDENT (TIMES)": 0,
        }
