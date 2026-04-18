import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from entries.models import BaggingInput  # Giả định tên model của bạn


class Command(BaseCommand):
    help = "Import dữ liệu Bagging từ Excel (Xử lý gộp dòng và 2 nhân viên)"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Đường dẫn file Excel")
        parser.add_argument("--save", action="store_true", help="Lưu vào DB")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        save_mode = options["save"]

        # 1. Đọc Excel
        df = pd.read_excel(file_path)
        self.stdout.write(self.style.NOTICE(f"Đang xử lý {len(df)} dòng dữ liệu thô..."))

        # 2. Logic Gộp Dòng (Grouping)
        # Chúng ta gộp theo: Date, Employee1, Employee2, Shift, Lot Number
        grouped = {}

        for _, row in df.iterrows():
            if pd.isna(row.get("Date")): continue

            # Chuẩn hóa ngày
            date_val = pd.to_datetime(row["Date"], dayfirst=True).date()

            # Tạo khóa định danh nhóm
            emp1 = str(row.get("Employee1", "")).strip()
            emp2 = str(row.get("Employee2", "")).strip() if pd.notna(row.get("Employee2")) else None
            shift = str(row.get("Shift", "Day")).strip()
            lot = str(row.get("Lot Number", "")).strip() if pd.notna(row.get("Lot Number")) else ""

            group_key = (date_val, emp1, emp2, shift, lot)

            if group_key not in grouped:
                grouped[group_key] = {
                    "date": date_val,
                    "employee_1": emp1,
                    "employee_2": emp2,
                    "shift": shift,
                    "lot_number": lot,
                    "production_data": []
                }

            # Thêm chi tiết sản phẩm vào mảng
            grouped[group_key]["production_data"].append({
                "productCode": str(row.get("Product Code", "")),
                "inputQty": int(row.get("Input", 0)),
                "outputQty": int(row.get("Output", 0))
            })

        # 3. Chuyển đổi thành danh sách Model Instance
        records = []
        for data in grouped.values():
            records.append(BaggingInput(
                date=data["date"],
                employee=data["employee_1"],
                employee_2=data["employee_2"],
                shift=data["shift"],
                lot_number=data["lot_number"],
                production_data=data["production_data"]
            ))

        # 4. Lưu vào Database
        if not save_mode:
            self.stdout.write(
                self.style.WARNING(f"Preview: Đã gộp thành {len(records)} bản ghi tổng hợp. Dùng --save để lưu."))
        else:
            with transaction.atomic():
                # Tùy chọn: Xóa dữ liệu cũ nếu cần
                BaggingInput.objects.all().delete()
                BaggingInput.objects.bulk_create(records, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"✅ Đã gộp và import {len(records)} bản ghi thành công!"))