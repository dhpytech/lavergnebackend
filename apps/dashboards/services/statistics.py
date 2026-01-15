class ProductionStats:
    def __init__(self, current_data, lm_data, ly_data, safety_curr, safety_lm, safety_ly):
        self.data = current_data
        self.lm = lm_data
        self.ly = ly_data
        self.safety = safety_curr
        self.safety_lm = safety_lm
        self.safety_ly = safety_ly

    def _get_raw(self, data, safety_vals):
        """Logic tính toán gốc của bạn"""
        p = {
            "prod": 0, "scrap": 0, "dlnc": 0, "reject": 0, "visslab": 0,
            "stop_hr": 0, "order_chg": 0, "mech_fail": 0, "mech_hr": 0, "off_days": 0
        }
        for d in data:
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

        num_shifts = len(set((d["date"], d["shift"]) for d in data))
        total_hr = (num_shifts - p["off_days"]) * 12

        # Các tỷ lệ
        used_pct = (total_hr - p["stop_hr"]) / total_hr if total_hr > 0 else 0
        yield_pct = p["prod"] / (p["prod"] + p["reject"] + p["scrap"]) if (p["prod"] + p["reject"] + p[
            "scrap"]) > 0 else 0
        net_hr = (p["prod"] + p["reject"] + p["scrap"] + p["visslab"]) / (total_hr - p["stop_hr"]) if (total_hr - p[
            "stop_hr"]) > 0 else 0

        return {**p, "used_pct": used_pct, "yield_pct": yield_pct, "net_hr": net_hr, "total_hr": total_hr,
                "incident": safety_vals['incident'], "accident": safety_vals['accident']}

    def _diff(self, curr, past):
        """Tính % chênh lệch"""
        if past == 0: return "0%"
        return f"{((curr - past) / past) * 100:+.1f}%"

    def calculate(self):
        c = self._get_raw(self.data, self.safety)
        l = self._get_raw(self.lm, self.safety_lm)
        y = self._get_raw(self.ly, self.safety_ly)

        # Trả về đúng thứ tự và cấu trúc bạn đã yêu cầu
        return {
            "PRODUCTION (KG)": {
                "value": f"{c['prod']:,.0f}",
                "lastMonth": self._diff(c['prod'], l['prod']),
                "lastYear": self._diff(c['prod'], y['prod'])
            },
            "SCRAP (KG)": {
                "value": f"{c['scrap']:,.1f}",
                "lastMonth": self._diff(c['scrap'], l['scrap']),
                "lastYear": self._diff(c['scrap'], y['scrap'])
            },
            "DL/NC (KG)": {
                "value": f"{c['dlnc']:,.0f}",
                "lastMonth": self._diff(c['dlnc'], l['dlnc']),
                "lastYear": self._diff(c['dlnc'], y['dlnc'])
            },
            "SCRAP/PRODUCTION (%)": {
                "value": f"{(c['scrap'] / c['prod'] * 100 if c['prod'] > 0 else 0):.2f}%",
                "lastMonth": self._diff((c['scrap'] / c['prod'] if c['prod'] > 0 else 0),
                                        (l['scrap'] / l['prod'] if l['prod'] > 0 else 0)),
                "lastYear": self._diff((c['scrap'] / c['prod'] if c['prod'] > 0 else 0),
                                       (y['scrap'] / y['prod'] if y['prod'] > 0 else 0))
            },
            "STOP TIME (HOUR)": {
                "value": f"{c['stop_hr']:.2f}",
                "lastMonth": self._diff(c['stop_hr'], l['stop_hr']),
                "lastYear": self._diff(c['stop_hr'], y['stop_hr'])
            },
            "NUMBER OF ORDER CHANGE": {
                "value": str(c["order_chg"]),
                "lastMonth": self._diff(c['order_chg'], l['order_chg']),
                "lastYear": self._diff(c['order_chg'], y['order_chg'])
            },
            "NUMBER OF MECHANICAL FAILURE": {
                "value": str(c["mech_fail"]),
                "lastMonth": self._diff(c['mech_fail'], l['mech_fail']),
                "lastYear": self._diff(c['mech_fail'], y['mech_fail'])
            },
            "NET/HOUR (KG/HOUR)": {
                "value": f"{c['net_hr']:.2f}",
                "lastMonth": self._diff(c['net_hr'], l['net_hr']),
                "lastYear": self._diff(c['net_hr'], y['net_hr'])
            },
            "UTILISATION (%)": {
                "value": f"{c['used_pct']:.2%}",
                "lastMonth": self._diff(c['used_pct'], l['used_pct']),
                "lastYear": self._diff(c['used_pct'], y['used_pct'])
            },
            "YIELD (%)": {
                "value": f"{c['yield_pct']:.2%}",
                "lastMonth": self._diff(c['yield_pct'], l['yield_pct']),
                "lastYear": self._diff(c['yield_pct'], y['yield_pct'])
            },
            "OEE (%)": {
                "value": f"{(c['used_pct'] * c['yield_pct']):.2%}",
                "lastMonth": self._diff(c['used_pct'] * c['yield_pct'], l['used_pct'] * l['yield_pct']),
                "lastYear": self._diff(c['used_pct'] * c['yield_pct'], y['used_pct'] * y['yield_pct'])
            },
            "MTTR (HOUR)": {
                "value": f"{(c['mech_hr'] / c['mech_fail'] if c['mech_fail'] > 0 else 0):.2f}",
                "lastMonth": self._diff((c['mech_hr'] / c['mech_fail'] if c['mech_fail'] > 0 else 0),
                                        (l['mech_hr'] / l['mech_fail'] if l['mech_fail'] > 0 else 0)),
                "lastYear": self._diff((c['mech_hr'] / c['mech_fail'] if c['mech_fail'] > 0 else 0),
                                       (y['mech_hr'] / y['mech_fail'] if y['mech_fail'] > 0 else 0))
            },
            "MTBF (HOUR)": {
                "value": f"{(c['total_hr'] / c['mech_fail'] if c['mech_fail'] > 0 else c['total_hr']):.2f}",
                "lastMonth": self._diff((c['total_hr'] / c['mech_fail'] if c['mech_fail'] > 0 else c['total_hr']),
                                        (l['total_hr'] / l['mech_fail'] if l['mech_fail'] > 0 else l['total_hr'])),
                "lastYear": self._diff((c['total_hr'] / c['mech_fail'] if c['mech_fail'] > 0 else c['total_hr']),
                                       (y['total_hr'] / y['mech_fail'] if y['mech_fail'] > 0 else y['total_hr']))
            },
            "INCIDENT (TIMES)": {
                "value": str(c['incident']),
                "lastMonth": f"{c['incident'] - l['incident']:+d}",
                "lastYear": f"{c['incident'] - y['incident']:+d}"
            },
            "ACCIDENT (TIMES)": {
                "value": str(c['accident']),
                "lastMonth": f"{c['accident'] - l['accident']:+d}",
                "lastYear": f"{c['accident'] - y['accident']:+d}"
            },
        }
