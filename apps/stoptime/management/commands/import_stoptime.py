import pandas as pd
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from stoptime.models import StopTime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import dữ liệu StopTime từ file Excel'

    def handle(self, *args, **kwargs):
        file_path = 'apps/stoptime/data/stoptime.xlsx'

        try:
            df = pd.read_excel(file_path).fillna('').map(
                lambda x: x.strip() if isinstance(x, str) else x
            )

            # Ánh xạ stop_time_name vào memory
            existing_stops = {s.stop_time_name: s for s in StopTime.objects.all()}

            to_create = []
            to_update = []

            for _, row in df.iterrows():
                name = str(row.get('stop_time_name', ''))
                desc = str(row.get('stop_time_description', ''))

                if not name:
                    continue

                if name in existing_stops:
                    obj = existing_stops[name]
                    if obj.stop_time_description != desc:
                        obj.stop_time_description = desc
                        to_update.append(obj)
                else:
                    to_create.append(StopTime(stop_time_name=name, stop_time_description=desc))

            with transaction.atomic():
                if to_create:
                    StopTime.objects.bulk_create(to_create, batch_size=500)
                if to_update:
                    StopTime.objects.bulk_update(to_update, ['stop_time_description'], batch_size=500)

            self.stdout.write(self.style.SUCCESS(
                f'StopTime: Tạo mới {len(to_create)}, Cập nhật {len(to_update)}.'
            ))

        except Exception as e:
            logger.error(f"Lỗi khi import StopTime: {e}")
            self.stdout.write(self.style.ERROR(f'Thất bại: {str(e)}'))
