import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from entries.models import MarisInput


class Command(BaseCommand):
    help = "Import dữ liệu Maris từ Excel vào DB"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Đường dẫn file Excel")
        parser.add_argument(
            "--sheet",
            type=str,
            default=0,
            help="Tên sheet hoặc chỉ số (0 = sheet đầu tiên). Mặc định = 0"
        )
        parser.add_argument(
            "--save",
            action="store_true",
            help="Nếu có cờ này thì sẽ lưu vào DB, mặc định chỉ test"
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name = options["sheet"]
        test_mode = not options["save"]  # mặc định test_mode = True

        # Đọc Excel (có dùng sheet_name)
        df = pd.read_excel(file_path, header=0, sheet_name=int(sheet_name))
        print("Columns:", df.columns.tolist())  # In ra danh sách cột để kiểm tra
        self.stdout.write(self.style.NOTICE(f"Đọc {len(df)} dòng dữ liệu từ {file_path}"))

        records = []

        for _, row in df.iterrows():
            # Bỏ qua dòng trống
            if pd.isna(row["Date"]):
                continue

            # ----- MAIN DATA (Production + Dl Nc Product + Reject/Scrap/Screen/Vis Slab) -----
            productions = []

            def split_to_dict(cell):
                """Chuyển 'CODE:VAL,CODE2:VAL2' thành dict {CODE: VAL}"""
                d = {}
                if pd.notna(cell):
                    for item in str(cell).split(","):
                        if ":" in item:
                            code, val = item.split(":", 1)
                            d[code.strip()] = val.strip()
                return d

            prods = split_to_dict(row.get("Production"))
            dlnc_raw = str(row.get("Dl Nc Product")) if pd.notna(row.get("Dl Nc Product")) else ""
            dlnc = split_to_dict(dlnc_raw.split("|", 1)[0]) if dlnc_raw else {}
            reject = split_to_dict(row.get("Reject Shaker"))
            scrap = split_to_dict(row.get("Scrap Die"))
            screen = split_to_dict(row.get("Screen Changer"))
            visslab = split_to_dict(row.get("Vis Slab"))

            # Case: nếu có thì áp dụng chung
            case_value = ""
            if "|" in dlnc_raw:
                parts = dlnc_raw.split("|", 1)
                if len(parts) > 1:
                    case_value = parts[1].strip()

            # Ghép dữ liệu cho từng productCode trong Production
            for code, qty in prods.items():
                productions.append({
                    "productCode": code,
                    "goodPro": qty,
                    "dlnc": dlnc.get(code, ""),  # nếu không có thì để ""
                    "case": case_value if case_value else "",  # nếu có thì gán, không thì ""
                    "reject": reject.get(code, ""),
                    "scrap": scrap.get(code, ""),
                    "screen": screen.get(code, ""),
                    "visslab": visslab.get(code, "")
                })

            # ----- STOP TIMES -----
            stop_times = []
            if pd.notna(row.get("StopTime")):
                for item in str(row["StopTime"]).split(","):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        stop_times.append({"stopTime": k.strip(), "hour": v.strip()})

            # ----- PROBLEMS -----
            problems = []
            if pd.notna(row.get("Problem")):
                for item in str(row["Problem"]).split(","):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        problems.append({"problem": k.strip(), "hour": v.strip()})

            # ----- COMMENT -----
            comment = row.get("Comment For Stop Time")
            comment = str(comment).strip() if pd.notna(comment) else None

            # ----- Shift + Employee xử lý NaN -----
            shift = row["Shift"] if pd.notna(row.get("Shift")) else None
            employee = row["Operator"] if pd.notna(row.get("Operator")) else None

            # ----- Tạo object -----
            records.append(MarisInput(
                # date=pd.to_datetime(row["Date"]).date(),
                date=pd.to_datetime(row["Date"], format="%d/%m/%Y").date(),
                shift=shift,
                employee=employee,
                mainData=productions if productions else [],  # JSONField không cho null
                stopTimes=stop_times if stop_times else None,
                problems=problems if problems else None,
                comment=comment
            ))

        # ----- Lưu DB hoặc Preview -----
        if test_mode:
            self.stdout.write(self.style.NOTICE("⚠️ Chế độ TEST: Dữ liệu chưa được lưu vào DB"))
            self.stdout.write(self.style.NOTICE("Preview 3 bản ghi đầu tiên:"))
            for i, r in enumerate(records[270:275], start=1):
                self.stdout.write(
                    self.style.NOTICE(
                        f"{i}. Date={r.date}, Shift={r.shift}, Employee={r.employee}, "
                        f"MainData={r.mainData}, StopTimes={r.stopTimes}, Problems={r.problems}, Comment={r.comment}"
                    )
                )
            self.stdout.write(self.style.WARNING(f"Tổng số bản ghi đọc được: {len(records)}"))
        else:
            with transaction.atomic():
                MarisInput.objects.bulk_create(records, batch_size=500)

            self.stdout.write(self.style.SUCCESS(f"✅ Đã import {len(records)} dòng vào DB"))
