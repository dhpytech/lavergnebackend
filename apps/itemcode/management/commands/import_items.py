import pandas as pd
from django.db import transaction, DatabaseError
from django.core.management.base import BaseCommand
from itemcode.models import ItemCode
import logging

# Thiết lập logger để truy vết lỗi
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import ItemCode chuyên nghiệp: Atomic Transaction + Bulk Operations'

    def handle(self, *args, **kwargs):
        file_path = 'apps/itemcode/data/itemcodes.xlsx'

        try:
            # 1. Đọc file Excel
            df = pd.read_excel(file_path)
            # Làm sạch dữ liệu cơ bản
            df = df.fillna('')  # Thay thế giá trị NaN bằng chuỗi trống
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # 2. Lấy dữ liệu hiện có để phân loại Create/Update
            # Lưu vào dictionary {item_name: object} để tìm kiếm với độ phức tạp O(1)
            existing_items = {item.item_name: item for item in ItemCode.objects.all()}

            to_create = []
            to_update = []

            self.stdout.write("Đang phân tích dữ liệu...")

            for index, row in df.iterrows():
                name = str(row['items_name'])
                desc = str(row['item_description'])
                i_type = str(row['item_type']).lower()

                # Validation đơn giản: Bỏ qua nếu không có tên vật tư
                if not name:
                    continue

                if name in existing_items:
                    # Nếu tồn tại -> Cập nhật
                    item = existing_items[name]
                    item.item_description = desc
                    item.item_type = i_type
                    to_update.append(item)
                else:
                    # Nếu chưa có -> Tạo mới
                    to_create.append(ItemCode(
                        item_name=name,
                        item_description=desc,
                        item_type=i_type
                    ))

            # 3. Thực thi Database với Atomic Transaction
            with transaction.atomic():
                self.stdout.write("Bắt đầu ghi vào Database (Atomic)...")

                if to_create:
                    ItemCode.objects.bulk_create(to_create, batch_size=1000)
                    self.stdout.write(self.style.SUCCESS(f' + Đã tạo mới {len(to_create)} dòng.'))

                if to_update:
                    # Chỉ cập nhật các trường được chỉ định
                    ItemCode.objects.bulk_update(
                        to_update,
                        ['item_description', 'item_type'],
                        batch_size=1000
                    )
                    self.stdout.write(self.style.SUCCESS(f' + Đã cập nhật {len(to_update)} dòng.'))

            self.stdout.write(self.style.SUCCESS('--- HOÀN TẤT IMPORT ---'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Lỗi: Không tìm thấy file tại {file_path}'))
        except DatabaseError as e:
            self.stdout.write(self.style.ERROR(f'Lỗi Database (Đã Rollback): {e}'))
            logger.error(f"Database error during import: {e}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi không xác định: {e}'))
            logger.exception("Unexpected error during import")
