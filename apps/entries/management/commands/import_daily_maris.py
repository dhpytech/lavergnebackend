from django.core.management.base import BaseCommand
from entries.models import MarisInput
from entries.signals import auto_calculate_maris_daily


class Command(BaseCommand):
    help = 'Tong hop du lieu lich su cho MarisDailySummary'

    def handle(self, *args, **options):
        # 1. Tim tat ca cac cap Ngay + Nhan vien duy nhat
        history = MarisInput.objects.values('date', 'employee').distinct()
        total = history.count()

        self.stdout.write(self.style.WARNING(f"Tim thay {total} muc can tong hop. Bat dau..."))

        # 2. Duyet qua tung muc
        for index, entry in enumerate(history, 1):
            d = entry['date']
            e = entry['employee']

            # Lay 1 ban ghi lam moi (trigger)
            target_obj = MarisInput.objects.filter(date=d, employee=e).first()

            if target_obj:
                # Goi truc tiep ham xu ly
                # kwargs={'created': False} de gia lap day la mot lenh update
                auto_calculate_maris_daily(sender=MarisInput, instance=target_obj)

                # In tien do theo kieu: [1/100] Da xong: 2026-04-27 | Nhan vien A
                self.stdout.write(f"[{index}/{total}] --- Da xong: {d} | {e}")

        self.stdout.write(self.style.SUCCESS("HOAN THANH CAP NHAT TOAN BO!"))