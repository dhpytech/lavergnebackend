class ProductionAggregator:
    @staticmethod
    def normalize(qs):
        normalized = []

        for r in qs:
            prod_list = r.production_data if (r.production_data and len(r.production_data) > 0) else [{}]

            for index, item in enumerate(prod_list):
                is_first = (index == 0)

                raw_outsource = item.get("outsource", False)
                if isinstance(raw_outsource, str):
                    outsource_bool = raw_outsource.lower() == "true"
                else:
                    outsource_bool = bool(raw_outsource)

                normalized.append({
                    "id": r.id,
                    "date": r.date,
                    "shift": r.shift,
                    "employee": r.employee,
                    "comment": r.comment if is_first else "",
                    "productCode": item.get("productCode"),
                    "goodPro": float(item.get("goodPro") or 0),
                    "screen": float(item.get("screenChanger") or 0) + float(item.get("screen") or 0),
                    "scrap": float(item.get("scrap") or 0),
                    "reject": float(item.get("reject") or 0),
                    "dlnc": float(item.get("dlnc") or 0) + float(item.get("DLNC") or 0),
                    "dlnc_case": str(item.get("dlnc_case") or "None").strip(),
                    "visslab": float(item.get("visslab") or 0) + float(item.get("visLab") or 0),
                    "outputSetting": float(item.get("outputSetting") or 0),
                    'outsource': outsource_bool,
                    "stopTimes": r.stop_time_data if is_first else [],
                    "problems": r.problem_data if is_first else []
                })
        return normalized