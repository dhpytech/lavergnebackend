class ProductionAggregator:
    @staticmethod
    def normalize(qs):
        normalized = []

        for r in qs:
            prod_list = r.production_data if (r.production_data and len(r.production_data) > 0) else [{}]

            for index, item in enumerate(prod_list):
                is_first = (index == 0)

                normalized.append({
                    "id": r.id,
                    "date": r.date,
                    "shift": r.shift,
                    "employee": r.employee,
                    "comment": r.comment,
                    "productCode": item.get("productCode"),
                    "goodPro": float(item.get("goodPro") or 0),
                    "screen": float(item.get("screenChanger") or 0) + float(item.get("screen") or 0),
                    "scrap": float(item.get("scrap") or 0),
                    "reject": float(item.get("reject") or 0),
                    "dlnc": float(item.get("dlnc") or 0) + float(item.get("DLNC") or 0),
                    "visslab": float(item.get("visslab") or 0) + float(item.get("visLab") or 0),
                    "outputSetting": float(item.get("outputSetting") or 0),
                    "stopTimes": r.stop_time_data if is_first else [],
                    "problems": r.problem_data if is_first else []
                })
        return normalized