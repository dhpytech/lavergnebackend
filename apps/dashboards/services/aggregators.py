# dashboards/services/aggregators.py

class ProductionAggregator:

    @staticmethod
    def normalize_record(record):
        main = record.get("mainData", {})

        good = float(main.get("goodPro", 0))
        reject = float(main.get("reject", 0))
        scrap = float(main.get("scrap", 0))
        dlnc = float(main.get("dlnc", 0))
        output = float(main.get("outputSetting", 0))

        net = good - reject - scrap - dlnc
        rate = net / output if output > 0 else 0

        return {
            "date": record["date"],
            "shift": record["shift"],
            "employee": record["employee"],
            "productCode": main.get("productCode"),
            "goodPro": good,
            "net": net,
            "rate": round(rate * 100, 2),
            "dlnc": dlnc,
            "stopTimes": record.get("stopTimes", []),
            "problems": record.get("problems", [])
        }
