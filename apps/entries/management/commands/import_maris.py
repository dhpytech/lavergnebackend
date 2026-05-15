import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from entries.models import MarisInput


class Command(BaseCommand):
    help = "Cập nhật Maris: Output Setting lồng hoàn toàn vào logic Production"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Đường dẫn file Excel")
        parser.add_argument("--sheet", type=str, default=0, help="Chỉ số sheet")
        parser.add_argument("--save", action="store_true", help="Lưu vào DB")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name_opt = options["sheet"]
        test_mode = not options["save"]

        df = pd.read_excel(file_path, header=0, sheet_name=sheet_name_opt)
        total_rows = len(df)
        self.stdout.write(self.style.NOTICE(f"--- Đang xử lý {total_rows} dòng ---"))

        def split_to_dict(cell):
            d = {}
            if pd.notna(cell) and str(cell).strip():
                for item in str(cell).split(","):
                    if ":" in item:
                        code, val = item.split(":", 1)
                        d[code.strip()] = val.strip()
            return d

        def parse_dlnc_with_cases(dlnc_raw):
            dlnc_dict, case_dict = {}, {}
            if not dlnc_raw or pd.isna(dlnc_raw): return dlnc_dict, case_dict
            for token in [t.strip() for t in str(dlnc_raw).split(",") if t.strip()]:
                if "|" in token:
                    left, case_part = token.split("|", 1)
                    left, case_part = left.strip(), case_part.strip()
                else:
                    left, case_part = token, ""
                if ":" in left:
                    code, val = left.split(":", 1)
                    dlnc_dict[code.strip()], case_dict[code.strip()] = val.strip(), case_part
            return dlnc_dict, case_dict

        #PHÂN TÍCH DỮ LIỆU
        prepared_records = []
        for _, row in df.iterrows():
            date_raw = row.get("Date") or row.get("NewDate")
            if pd.isna(date_raw): continue

            productions = []
            # CHỈ KHI CÓ PRODUCTION MỚI XỬ LÝ CÁC DỮ LIỆU LIÊN QUAN
            if pd.notna(row.get("Production")):
                prods = split_to_dict(row.get("Production"))

                # Load tất cả phụ trợ (chỉ khi có sản xuất)
                dlnc_dict, case_dict = parse_dlnc_with_cases(row.get("Dl Nc Product"))
                reject_dict = split_to_dict(row.get("Reject Shaker"))
                scrap_dict = split_to_dict(row.get("Scrap Die"))
                screen_dict = split_to_dict(row.get("Screen Changer"))
                visslab_dict = split_to_dict(row.get("Vis Slab"))

                # Load Output Setting để tra cứu
                os_dict = split_to_dict(row.get("Output Setting"))

                for code, qty in prods.items():
                    # Output Setting được "đẻ" ra từ chính mã code của Production
                    productions.append({
                        "productCode": code,
                        "goodPro": qty,
                        "outputSetting": os_dict.get(code, ""),  # Lồng trực tiếp
                        "dlnc": dlnc_dict.get(code, ""),
                        "dlnc_case": case_dict.get(code, ""),
                        "reject": reject_dict.get(code, ""),
                        "scrap": scrap_dict.get(code, ""),
                        "screen": screen_dict.get(code, ""),
                        "visslab": visslab_dict.get(code, ""),
                    })

            # Dữ liệu Stop/Problem xử lý độc lập
            stop_times = [{"stopTime": k, "hour": v} for k, v in split_to_dict(row.get("StopTime")).items()]
            problems = [{"problem": k, "hour": v} for k, v in split_to_dict(row.get("Problem")).items()]

            try:
                date_val = pd.to_datetime(date_raw, dayfirst=True).date()
            except:
                continue

            prepared_records.append({
                "date": date_val,
                "shift": str(row.get("Shift", "DAY")).strip(),
                "employee": str(row.get("Operator", "")).strip(),
                "defaults": {
                    "production_data": productions,
                    "stop_time_data": stop_times,
                    "problem_data": problems,
                    "comment": str(row.get("Comment For Stop Time", "")).strip(),
                }
            })

        # BƯỚC 2: GHI VÀO DB (CHIA BATCH 100 ĐỂ THEO DÕI)
        if test_mode:
            self.stdout.write(self.style.WARNING(f"Preview OK: {len(prepared_records)} dòng."))
        else:
            batch_size = 500
            for i in range(0, len(prepared_records), batch_size):
                batch = prepared_records[i: i + batch_size]
                with transaction.atomic():
                    for item in batch:
                        MarisInput.objects.update_or_create(
                            date=item["date"], shift=item["shift"], employee=item["employee"],
                            defaults=item["defaults"]
                        )
                self.stdout.write(f"✅ Đã lưu đợt: {min(i + batch_size, len(prepared_records))}/{len(prepared_records)}")

        self.stdout.write(self.style.SUCCESS("🏁 Xong!"))
