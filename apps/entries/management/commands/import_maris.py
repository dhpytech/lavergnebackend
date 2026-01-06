import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from entries.models import MarisInput

class Command(BaseCommand):
    help = "Import dữ liệu Maris từ Excel vào DB (Khớp Model Snake Case)"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Đường dẫn file Excel")
        parser.add_argument("--sheet", type=str, default=0, help="Chỉ số sheet (0, 1, 2...)")
        parser.add_argument("--save", action="store_true", help="Lưu vào DB")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name_opt = options["sheet"]
        test_mode = not options["save"]

        try:
            sheet_name = int(sheet_name_opt)
        except Exception:
            sheet_name = sheet_name_opt

        df = pd.read_excel(file_path, header=0, sheet_name=sheet_name)
        self.stdout.write(self.style.NOTICE(f"Đang xử lý {len(df)} dòng từ: {file_path}"))

        records = []

        def split_to_dict(cell):
            d = {}
            if pd.notna(cell):
                for item in str(cell).split(","):
                    item = item.strip()
                    if ":" in item:
                        code, val = item.split(":", 1)
                        d[code.strip()] = val.strip()
            return d

        def parse_dlnc_with_cases(dlnc_raw):
            dlnc_dict = {}
            case_dict = {}
            if not dlnc_raw or pd.isna(dlnc_raw):
                return dlnc_dict, case_dict
            for token in [t.strip() for t in str(dlnc_raw).split(",") if t.strip()]:
                if "|" in token:
                    left, case_part = token.split("|", 1)
                    left, case_part = left.strip(), case_part.strip()
                else:
                    left, case_part = token, ""
                if ":" in left:
                    code, val = left.split(":", 1)
                    dlnc_dict[code.strip()] = val.strip()
                    case_dict[code.strip()] = case_part
            return dlnc_dict, case_dict

        for _, row in df.iterrows():
            if pd.isna(row.get("Date")):
                continue

            # 1. Xử lý PRODUCTION_DATA (Snake Case)
            productions = []
            if pd.notna(row.get("Production")):
                prods = split_to_dict(row.get("Production"))
                dlnc_dict, case_dict = parse_dlnc_with_cases(row.get("Dl Nc Product"))
                reject_dict = split_to_dict(row.get("Reject Shaker"))
                scrap_dict = split_to_dict(row.get("Scrap Die"))
                screen_dict = split_to_dict(row.get("Screen Changer"))
                visslab_dict = split_to_dict(row.get("Vis Slab"))
                output_setting_dict = split_to_dict(row.get("Output Setting"))

                for code, qty in prods.items():
                    productions.append({
                        "productCode": code,
                        "goodPro": qty,
                        "dlnc": dlnc_dict.get(code, ""),
                        "dlnc_case": case_dict.get(code, ""), # Đổi tên cho khớp logic Frontend
                        "reject": reject_dict.get(code, ""),
                        "scrap": scrap_dict.get(code, ""),
                        "screen": screen_dict.get(code, ""),
                        "visslab": visslab_dict.get(code, ""),
                        "outputSetting": output_setting_dict.get(code, "") # Bổ sung Output Setting
                    })

            # 2. Xử lý STOP_TIME_DATA (Snake Case)
            stop_times = []
            if pd.notna(row.get("StopTime")):
                for item in str(row["StopTime"]).split(","):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        stop_times.append({"stopTime": k.strip(), "hour": v.strip()})

            # 3. Xử lý PROBLEM_DATA (Snake Case)
            problems = []
            if pd.notna(row.get("Problem")):
                for item in str(row["Problem"]).split(","):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        problems.append({"problem": k.strip(), "hour": v.strip()})

            # 4. Thông tin chung
            comment = str(row.get("Comment For Stop Time")).strip() if pd.notna(row.get("Comment For Stop Time")) else None
            shift = row["Shift"] if pd.notna(row.get("Shift")) else "DAY"
            employee = row["Operator"] if pd.notna(row.get("Operator")) else None

            try:
                date_val = pd.to_datetime(row["Date"], format="%d/%m/%Y").date()
            except Exception:
                date_val = pd.to_datetime(row["Date"], dayfirst=True).date()

            # KHỚP CHÍNH XÁC VỚI MODEL TRONG MODELS.PY
            records.append(MarisInput(
                date=date_val,
                shift=shift,
                employee=employee,
                production_data=productions,      # Sửa từ mainData
                stop_time_data=stop_times,        # Sửa từ stopTimes
                problem_data=problems,            # Sửa từ problems
                comment=comment
            ))

        if test_mode:
            self.stdout.write(self.style.NOTICE(f"Preview: Tìm thấy {len(records)} bản ghi. Chạy với --save để lưu."))
        else:
            with transaction.atomic():
                MarisInput.objects.all().delete()
                MarisInput.objects.bulk_create(records, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"✅ Đã import {len(records)} bản ghi thành công."))
