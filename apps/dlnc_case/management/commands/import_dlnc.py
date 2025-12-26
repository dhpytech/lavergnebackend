import pandas as pd
from django.db import transaction, DatabaseError
from django.core.management.base import BaseCommand
from dlnc_case.models import DlncCase
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import DlncCase với dlnc_case_name là Primary Key'

    def handle(self, *args, **kwargs):
        file_path = 'apps/dlnc_case/data/dlnc.xlsx'

        try:
            df = pd.read_excel(file_path)
            df = df.fillna('')
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Truy vấn toàn bộ để đưa vào memory (Tối ưu cho dữ liệu lớn)
            existing_cases = {case.pk: case for case in DlncCase.objects.all()}

            to_create = []
            to_update = []

            for index, row in df.iterrows():
                name = str(row.get('dlnc_case_name', '')).strip()
                desc = str(row.get('dlnc_case_description', '')).strip()

                if not name:
                    continue

                if name in existing_cases:
                    # Nếu tên đã tồn tại (Khóa chính đã có) -> Kiểm tra xem có cần cập nhật description không
                    case = existing_cases[name]
                    if case.dlnc_case_description != desc:
                        case.dlnc_case_description = desc
                        to_update.append(case)
                else:
                    # Nếu tên chưa có trong DB -> Tạo mới
                    to_create.append(DlncCase(
                        dlnc_case_name=name,
                        dlnc_case_description=desc
                    ))

            # Thực thi ghi dữ liệu an toàn
            with transaction.atomic():
                if to_create:
                    DlncCase.objects.bulk_create(to_create, batch_size=1000)
                    self.stdout.write(self.style.SUCCESS(f' + Đã tạo mới {len(to_create)} bản ghi.'))

                if to_update:
                    DlncCase.objects.bulk_update(to_update, ['dlnc_case_description'], batch_size=1000)
                    self.stdout.write(self.style.SUCCESS(f' + Đã cập nhật {len(to_update)} bản ghi.'))

            self.stdout.write(self.style.SUCCESS('--- HOÀN TẤT ---'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Sự cố: {str(e)}'))
