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
        sheet_name_opt = options["sheet"]
        test_mode = not options["save"]  # mặc định test_mode = True

        # sheet_name có thể là số hoặc tên -> thử convert sang int nếu được
        try:
            sheet_name = int(sheet_name_opt)
        except Exception:
            sheet_name = sheet_name_opt

        # Đọc Excel (có dùng sheet_name)
        df = pd.read_excel(file_path, header=0, sheet_name=sheet_name)
        print("Columns:", df.columns.tolist())  # In ra danh sách cột để kiểm tra
        self.stdout.write(self.style.NOTICE(f"Đọc {len(df)} dòng dữ liệu từ {file_path}"))

        records = []

        def split_to_dict(cell):
            """
            Chuyển 'CODE:VAL,CODE2:VAL2' thành dict {CODE: VAL}.
            Trả {} nếu cell rỗng/NaN.
            """
            d = {}
            if pd.notna(cell):
                for item in str(cell).split(","):
                    item = item.strip()
                    if ":" in item:
                        code, val = item.split(":", 1)
                        d[code.strip()] = val.strip()
            return d

        def parse_dlnc_with_cases(dlnc_raw):
            """
            Parse Dl Nc Product thành:
              - dlnc_dict: { code: dlnc_value }
              - case_dict: { code: case_value }  (case_value = "" nếu token không có |Case)
            Quy tắc:
              - Mỗi token có dạng "CODE:VAL" hoặc "CODE:VAL|Case"
              - Nếu token có "|Case" thì case gán cho đúng mã đó.
              - Nếu token không có "|Case" thì mã đó có case = "".
              - Các mã trong Production mà không xuất hiện trong Dl Nc Product => dlnc="", case=""
            """
            dlnc_dict = {}
            case_dict = {}
            if not dlnc_raw or pd.isna(dlnc_raw):
                return dlnc_dict, case_dict

            for token in [t.strip() for t in str(dlnc_raw).split(",") if t.strip()]:
                # token có thể là "CODE:VAL" hoặc "CODE:VAL|Case"
                if "|" in token:
                    left, case_part = token.split("|", 1)
                    left = left.strip()
                    case_part = case_part.strip()
                else:
                    left = token
                    case_part = ""

                if ":" in left:
                    code, val = left.split(":", 1)
                    code = code.strip()
                    val = val.strip()
                    dlnc_dict[code] = val
                    case_dict[code] = case_part  # nếu case_part == "" thì rỗng

            return dlnc_dict, case_dict

        for _, row in df.iterrows():
            # Bỏ qua dòng trống
            if pd.isna(row.get("Date")):
                continue

            # ----- MAIN DATA (Production + Dl Nc Product + Reject/Scrap/Screen/Vis Slab) -----
            productions = []

            if pd.notna(row.get("Production")):
                # parse production (có thể nhiều code)
                prods = split_to_dict(row.get("Production"))

                # parse DLNC (per-code + có thể per-code case)
                dlnc_raw = row.get("Dl Nc Product")
                dlnc_dict, case_dict = parse_dlnc_with_cases(dlnc_raw)

                # parse các cột khác thành per-code dict
                reject_dict = split_to_dict(row.get("Reject Shaker"))
                scrap_dict = split_to_dict(row.get("Scrap Die"))
                screen_dict = split_to_dict(row.get("Screen Changer"))
                visslab_dict = split_to_dict(row.get("Vis Slab"))

                # Ghép dữ liệu cho từng productCode trong Production
                for code, qty in prods.items():
                    productions.append({
                        "productCode": code,
                        "goodPro": qty,
                        "dlnc": dlnc_dict.get(code, ""),      # nếu không có -> ""
                        "case": case_dict.get(code, ""),      # nếu không có -> ""
                        "reject": reject_dict.get(code, ""),
                        "scrap": scrap_dict.get(code, ""),
                        "screen": screen_dict.get(code, ""),
                        "visslab": visslab_dict.get(code, "")
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

            # ----- Parse date (ưu tiên format dd/mm/YYYY, fallback dayfirst) -----
            try:
                date_val = pd.to_datetime(row["Date"], format="%d/%m/%Y").date()
            except Exception:
                date_val = pd.to_datetime(row["Date"], dayfirst=True).date()

            # ----- Tạo object -----
            records.append(MarisInput(
                date=date_val,
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
            self.stdout.write(self.style.NOTICE("Preview các bản ghi (ví dụ 270->275):"))
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
