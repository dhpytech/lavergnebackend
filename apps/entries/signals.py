# maris/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MarisInput, MarisDailySummary
from dashboards.services.aggregators import ProductionAggregator
from dashboards.services.statistics import ProductionStats


@receiver(post_save, sender=MarisInput)
@receiver(post_delete, sender=MarisInput)
def auto_calculate_maris_daily(sender, instance, **kwargs):
    date = instance.date
    employee = instance.employee.strip() if instance.employee else "Unknown"

    # 1. Lấy QuerySet thô
    qs = MarisInput.objects.filter(date=date, employee=employee)

    if qs.exists():
        # 2. Sử dụng Aggregator của bạn để làm sạch dữ liệu
        normalized = ProductionAggregator.normalize(qs)

        # 3. Sử dụng ProductionStats để gom nhóm số liệu thô (chế độ lấy số liệu thực tế)
        # Chúng ta truyền mảng rỗng cho LM/LY vì chỉ đang tính cho ngày hiện tại
        safety_zero = {'incident': 0, 'accident': 0}
        stats = ProductionStats(normalized, [], [], safety_zero, safety_zero, safety_zero)

        # Lấy kết quả từ hàm _get_raw (hàm này tính toán các giá trị cộng dồn)
        c = stats._get_raw(normalized, safety_zero)

        # 4. Lưu/Cập nhật vào bảng Summary
        MarisDailySummary.objects.update_or_create(
            date=date, employee=employee,
            defaults={
                'prod': c['prod'],
                'scrap': c['scrap'],
                'dlnc': c['dlnc'],
                'reject': c['reject'],
                'screen': c['screen'],
                'visslab': c['visslab'],
                'stop_hr': c['stop_hr'],
                'off_hours': c['off_hours'],
                'mech_hr': c['mech_hr'],
                'order_chg': c['order_chg'],
                'mech_fail': c['mech_fail'],
                'num_shifts': len(set([f"{d['date']}-{d['shift']}" for d in normalized]))
            }
        )
    else:
        # Nếu xóa hết dữ liệu thô thì xóa luôn dòng tổng hợp
        MarisDailySummary.objects.filter(date=date, employee=employee).delete()