# your_project/apps/dashboard/services.py
from datetime import datetime


class BaggingDetailDashboardService:
    @classmethod
    def get_analytics(cls, queryset, view_type='monthly'):
        if view_type == 'daily':
            time_format = "%Y-%m-%d"
            label_format = "%d/%m/%Y"
        else:
            time_format = "%Y-%m"
            label_format = "Tháng %m/%Y"
        raw_map = {}

        for entry in queryset:
            t_key = entry.date.strftime(time_format)
            t_label = entry.date.strftime(label_format)

            if t_key not in raw_map:
                raw_map[t_key] = {
                    "time_key": t_key,
                    "label": t_label,
                    "summary": {
                        "total_in": 0.0,
                        "total_out": 0.0,
                        "total_time": 0,
                    },
                    "details": {}
                }

            active_emps = [e for e in [entry.employee, entry.employee_2] if e]
            num_emps = len(active_emps)
            if num_emps == 0:
                continue

            for emp_name in active_emps:
                if emp_name not in raw_map[t_key]["details"]:
                    raw_map[t_key]["details"][emp_name] = {
                        "in": 0.0,
                        "out": 0.0,
                        "time": 0
                    }

                raw_map[t_key]["details"][emp_name]["time"] += 12
                raw_map[t_key]["summary"]["total_time"] += 12

                for item in (entry.production_data or []):
                    iq = float(item.get('inputQty') or 0) / num_emps
                    oq = float(item.get('outputQty') or 0) / num_emps

                    raw_map[t_key]["details"][emp_name]["in"] += iq
                    raw_map[t_key]["details"][emp_name]["out"] += oq

                    raw_map[t_key]["summary"]["total_in"] += iq
                    raw_map[t_key]["summary"]["total_out"] += oq

        final_list = []
        sort_date_format = "%Y-%m-%d" if view_type == 'daily' else "%Y-%m"

        for t_key in sorted(raw_map.keys(), key=lambda x: datetime.strptime(x, sort_date_format)):
            period_data = raw_map[t_key]

            s_in = period_data["summary"]["total_in"]
            s_out = period_data["summary"]["total_out"]
            period_data["summary"]["rate"] = round((s_out / s_in * 100), 2) if s_in > 0 else 0.0

            period_data["summary"]["total_in"] = round(s_in, 1)
            period_data["summary"]["total_out"] = round(s_out, 1)

            processed_details = []
            for emp_name, emp_stats in period_data["details"].items():
                e_in = emp_stats["in"]
                e_out = emp_stats["out"]

                emp_stats["name"] = emp_name
                emp_stats["rate"] = round((e_out / e_in * 100), 2) if e_in > 0 else 0.0

                emp_stats["in"] = round(e_in, 1)
                emp_stats["out"] = round(e_out, 1)

                processed_details.append(emp_stats)

            period_data["details"] = processed_details
            final_list.append(period_data)

        return {
            "type": view_type,
            "data": final_list,
            "metric_configs": [
                {"id": "IN", "label": "Total Input", "unit": "kg"},
                {"id": "OUT", "label": "Total Output", "unit": "kg"},
                {"id": "TIME", "label": "Working Time", "unit": "h"},
                {"id": "RATE", "label": "Rate", "unit": "%"},
            ]
        }
