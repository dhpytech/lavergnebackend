class ProductionStats:
    def __init__(self, current_data, lm_data, ly_data, safety_curr, safety_lm, safety_ly):
        self.data = current_data
        self.lm = lm_data
        self.ly = ly_data
        self.safety = safety_curr
        self.safety_lm = safety_lm
        self.safety_ly = safety_ly

    def _get_raw(self, data, safety_vals):
        p = {"goodPro": 0, "prod": 0, "scrap": 0, "scrapDie": 0, "dlnc": 0, "reject": 0, "screen": 0, "visslab": 0, "stop_hr": 0, "order_chg": 0,
             "mech_fail": 0, "mech_hr": 0, "off_days": 0, "off_hours": 0, "stop_hr_no_weekend": 0, 'output_setting': 0,
             "perfect_time": 0, }

        active_shifts = set()
        dlnc_cases_map = {}
        stop_details = []
        problem_details = []
        comments = []

        for d in data:
            p["prod"] += d["goodPro"] + d["dlnc"]
            p["goodPro"] += d["goodPro"]
            p["scrapDie"] += d["scrap"]
            p["scrap"] += d["scrap"] + d["screen"]
            p["dlnc"] += d["dlnc"]
            p["reject"] += d["reject"]
            p["screen"] += d["screen"]
            p["visslab"] += d["visslab"]
            p["output_setting"] += d["outputSetting"]
            each_perfect_time = (d["goodPro"]+d["dlnc"]+d["scrap"]+d["screen"]+d["reject"])/d["outputSetting"] if d["outputSetting"] else 0
            p["perfect_time"] += each_perfect_time

            case_name = d.get("dlnc_case", "None")
            if d["dlnc"] > 0 and case_name.lower() != "none":
                dlnc_cases_map[case_name] = dlnc_cases_map.get(case_name, 0.0) + d["dlnc"]

            if d.get("employee") and d.get("employee").strip():
                active_shifts.add(f'{d["date"]} - {d["shift"]}')

            if d.get("stopTimes"):
                stop_details.extend(d["stopTimes"])
            if d.get("problems"):
                problem_details.extend(d["problems"])

            if d.get("comment"):
                comments.append(d["comment"])

            stops = d.get("stopTimes")
            STOP_CODE_MAP = {
                "OFF_DAYS": ["HOLIDAY", "WEEKEND OFF"],
                "MECH_TIME": ["MECHANICAL/ELECTRICAL FAILURE"],
                "COUNTERS": ["# ORDER CHANGE", "# OF MECHANICAL FAILURE"]
            }

            for s in stops:
                hr = float(s.get("duration") or 0) or float(s.get("hour") or 0)
                st = str(s.get("stopTime") or s.get("stopCode")).strip()
                st_upper = st.upper()

                if not st.startswith("#"):
                    p["stop_hr"] += hr

                if st_upper in STOP_CODE_MAP["OFF_DAYS"]:
                    p["off_days"] += 1
                    p["off_hours"] += hr

                if st == "MECHANICAL/ELECTRICAL FAILURE":
                    p["mech_hr"] += hr

                if st == "# ORDER CHANGE":
                    p["order_chg"] += 1

                if st == "# OF MECHANICAL FAILURE":
                    p["mech_fail"] += 1

        p['stop_hr_no_weekend'] = p['stop_hr'] - p["off_hours"]

        num_shifts = len(active_shifts)
        total_hr = num_shifts * 12
        run_time = total_hr - p['stop_hr_no_weekend']

        total_output = p["prod"]+p["scrap"]+p["reject"]
        total_input = p["prod"]+p["scrap"]+p["reject"]+p["visslab"]
        total_setting = p['output_setting']

        used_pct = run_time / total_hr if total_hr > 0 else 0
        yield_pct = p["prod"] / total_input if total_input > 0 else 0
        net_hr = total_output/run_time if run_time > 0 else 0

        rate = p["perfect_time"]/run_time if run_time > 0 else 0

        return {
            **p, "used_pct": used_pct, "yield_pct": yield_pct, "rate": rate, "net_hr": net_hr, "total_hr": total_hr,
            "num_shifts": num_shifts, "total_setting": total_setting, "total_output": total_output,
            "incident": safety_vals['incident'], "accident": safety_vals['accident'],
            "dlnc_cases": dlnc_cases_map, "stop_details_list": stop_details, "problem_details_list": problem_details,
            "comments": comments,
        }

    def _diff(self, curr, past):
        if past == 0 : return "0%"
        return f"{((curr - past) / past) * 100:+.1f}%"

    def calculate(self):
        c = self._get_raw(self.data, self.safety)
        l = self._get_raw(self.lm, self.safety_lm)
        y = self._get_raw(self.ly, self.safety_ly)

        return {
            "PRODUCTION (KG)": {
                "value": f"{c['prod']:,.0f}",
                "lastMonth": self._diff(c['prod'], l['prod']),
                "lastYear": self._diff(c['prod'], y['prod'])
            },
            "DL/NC (KG)": {
                "value": f"{c['dlnc']:,.0f}",
                "lastMonth": self._diff(c['dlnc'], l['dlnc']),
                "lastYear": self._diff(c['dlnc'], y['dlnc'])
            },
            "SCRAP (KG)": {
                "value": f"{c['scrap']:,.1f}",
                "lastMonth": self._diff(c['scrap'], l['scrap']),
                "lastYear": self._diff(c['scrap'], y['scrap'])
            },
            "SCRAP/PRODUCTION (%)": {
                "value": f"{(c['scrap'] / c['prod'] * 100 if c['prod'] > 0 else 0):.2f}%",
                "lastMonth": self._diff((c['scrap'] / c['prod'] if c['prod'] > 0 else 0),
                                        (l['scrap'] / l['prod'] if l['prod'] > 0 else 0)),
                "lastYear": self._diff((c['scrap'] / c['prod'] if c['prod'] > 0 else 0),
                                       (y['scrap'] / y['prod'] if y['prod'] > 0 else 0))
            },
            "VISSLAB (KG)": {
                "value": f"{c['visslab']:,.1f}",
                "lastMonth": self._diff(c['visslab'], l['visslab']),
                "lastYear": self._diff(c['visslab'], y['visslab'])
            },
            "STOP TIME (HOUR)": {
                "value": f"{c["stop_hr"]:.2f} ({c["stop_hr_no_weekend"]:.2f} + {c["off_hours"]:.2f} )",
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
                "value": f"{(c['used_pct'] * c['yield_pct'] * c['rate']):.2%}",
                "lastMonth": self._diff(c['used_pct']*c['yield_pct']*c['rate'], l['used_pct']*l['yield_pct']*l['rate']),
                "lastYear": self._diff(c['used_pct']*c['yield_pct']*c['rate'], y['used_pct']*y['yield_pct']*y['rate'])
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
            # === ĐÂY CHÍNH LÀ NƠI TRẢ VỀ ĐỂ DÙNG CHO CÁC PHẦN BÁO CÁO SAU TẠI FRONTEND ===
            "dlnc_cases_breakdown": c["dlnc_cases"],
            "raw_normalized_list": self.data,
            "stop_details_list": c["stop_details_list"],
            "problem_details_list": c["problem_details_list"]
        }
