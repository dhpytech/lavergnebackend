import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from entries.models import MetalInput  # Đảm bảo bạn đã tạo Model này


class Command(BaseCommand):
    help = "Import dữ liệu Metal từ Excel (Gộp dòng theo Employee và Lot)"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Đường dẫn file Excel Metal")
        parser.add_argument("--save", action="store_true", help="Lưu vào DB")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        save_mode = options["save"]

        df = pd.read_excel(file_path)
        self.stdout.write(self.style.NOTICE(f"Đang xử lý {len(df)} dòng dữ liệu Metal..."))

        grouped = {}

        for _, row in df.iterrows():
            if pd.isna(row.get("Date")): continue

            # Chuẩn hóa Date
            date_val = pd.to_datetime(row["Date"], dayfirst=True).date()

            # Khóa gộp: Date + Employee + Shift + Lot Number
            # Lưu ý: Metal chỉ có 1 nhân viên theo file Excel bạn gửi
            emp = str(row.get("Employee", "")).strip()
            shift = str(row.get("Shift", "Day")).strip()
            lot = str(row.get("Lot Number", "")).strip()

            group_key = (date_val, emp, shift, lot)

            if group_key not in grouped:
                grouped[group_key] = {
                    "date": date_val,
                    "employee": emp,
                    "shift": shift,
                    "lot_number": lot,
                    "production_data": []
                }

            # Thêm chi tiết sản phẩm và cột ACTION đặc thù của Metal
            grouped[group_key]["production_data"].append({
                "productCode": str(row.get("Product Code", "")),
                "action": str(row.get("Action", "Origin")),
                "inputQty": int(row.get("Input", 0)),
                "outputQty": int(row.get("Output", 0))
            })

        records = []
        for data in grouped.values():
            records.append(MetalInput(
                date=data["date"],
                employee=data["employee"],
                shift=data["shift"],
                lot_number=data["lot_number"],
                production_data=data["production_data"]
            ))

        if not save_mode:
            self.stdout.write(
                self.style.WARNING(f"Preview: Gộp thành {len(records)} bản ghi Metal. Dùng --save để lưu."))
        else:
            with transaction.atomic():
                MetalInput.objects.bulk_create(records, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"✅ Đã import {len(records)} bản ghi Metal thành công!"))