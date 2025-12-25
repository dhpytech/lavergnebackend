import pandas as pd
from django.db import transaction, DatabaseError
from django.core.management.base import BaseCommand
from employee.models import Employee
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import danh sách nhân viên: Atomic Transaction + Bulk Operations'

    def handle(self, *args, **kwargs):
        # Đường dẫn file excel (Điều chỉnh theo thực tế của bạn)
        file_path = 'apps/employee/data/employee.xlsx'

        try:
            df = pd.read_excel(file_path)
            df = df.fillna('')
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # 2. Sử dụng employee_id làm Key vì nó là Primary Key
            existing_employees = {emp.employee_id: emp for emp in Employee.objects.all()}

            to_create = []
            to_update = []

            self.stdout.write("Đang phân tích dữ liệu nhân viên...")

            for index, row in df.iterrows():
                try:
                    e_id = str(row['employee_id'])
                    e_name = str(row['employee_name'])
                    e_pos = str(row['employee_position'])

                    if not e_id:
                        continue

                    if e_id in existing_employees:
                        # Cập nhật thông tin nhân viên cũ
                        emp = existing_employees[e_id]
                        emp.employee_name = e_name
                        emp.employee_position = e_pos
                        to_update.append(emp)
                    else:
                        # Thêm nhân viên mới
                        to_create.append(Employee(
                            employee_id=e_id,
                            employee_name=e_name,
                            employee_position=e_pos
                        ))
                except (ValueError, KeyError) as e:
                    self.stdout.write(self.style.WARNING(f"Bỏ qua dòng {index}: Dữ liệu ID không hợp lệ."))
                    continue

            # 3. Ghi vào Database với Atomic
            with transaction.atomic():
                if to_create:
                    Employee.objects.bulk_create(to_create, batch_size=1000)
                    self.stdout.write(self.style.SUCCESS(f' + Đã tạo mới {len(to_create)} nhân viên.'))

                if to_update:
                    Employee.objects.bulk_update(
                        to_update,
                        ['employee_name', 'employee_position'],
                        batch_size=1000
                    )
                    self.stdout.write(self.style.SUCCESS(f' + Đã cập nhật {len(to_update)} nhân viên.'))

            self.stdout.write(self.style.SUCCESS('--- HOÀN TẤT IMPORT EMPLOYEE ---'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Không tìm thấy file tại {file_path}'))
        except DatabaseError as e:
            self.stdout.write(self.style.ERROR(f'Lỗi Database: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi: {e}'))
