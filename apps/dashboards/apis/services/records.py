

def get_records(model_cls, start, end, shift=None):
    qs = model_cls.objects.filter(date__range=[start, end])

    if shift and shift != "Total":
        qs = qs.filter(shift=shift)

    records = []
    for r in qs:
        records.append({
            "date": r.date,
            "shift": r.shift,
            "mainData": r.production_data or [],
            "stopTimes": getattr(r, "stop_time_data", []) or [],
            "problems": getattr(r, "problem_data", []) or [],
        })

    return records
