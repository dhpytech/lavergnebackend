import pandas as pd
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from problems.models import Problem

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import dữ liệu Problem từ file Excel'

    def handle(self, *args, **kwargs):
        file_path = 'apps/problems/data/problems.xlsx'  # Cập nhật đường dẫn file

        try:
            df = pd.read_excel(file_path).fillna('').map(
                lambda x: x.strip() if isinstance(x, str) else x
            )

            # Lấy dữ liệu hiện tại đưa vào memory để tối ưu tốc độ kiểm tra
            existing_problems = {p.problem_code: p for p in Problem.objects.all()}

            to_create = []
            to_update = []

            for _, row in df.iterrows():
                code = str(row.get('problem_code', ''))
                name = str(row.get('problem_name', ''))

                if not code:
                    continue

                if code in existing_problems:
                    obj = existing_problems[code]
                    if obj.problem_name != name:
                        obj.problem_name = name
                        to_update.append(obj)
                else:
                    to_create.append(Problem(problem_code=code, problem_name=name))

            with transaction.atomic():
                if to_create:
                    Problem.objects.bulk_create(to_create, batch_size=500)
                if to_update:
                    Problem.objects.bulk_update(to_update, ['problem_name'], batch_size=500)

            self.stdout.write(self.style.SUCCESS(
                f'Problem: Tạo mới {len(to_create)}, Cập nhật {len(to_update)}.'
            ))

        except Exception as e:
            logger.error(f"Lỗi khi import Problem: {e}")
            self.stdout.write(self.style.ERROR(f'Thất bại: {str(e)}'))
