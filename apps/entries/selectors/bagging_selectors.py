from ..models import BaggingInput


def get_bagging_entries_selector(*, start_date=None, end_date=None, shift=None, lot_number=None):
    """
    Truy vấn dữ liệu thô.
    Sử dụng tham số tường minh (explicit arguments) thay vì dict chung chung để dễ debug.
    """
    queryset = BaggingInput.objects.all()

    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])

    if shift and shift != "All":
        queryset = queryset.filter(shift=shift)

    if lot_number:
        queryset = queryset.filter(lot_number__icontains=lot_number)

    return queryset.order_by('-date', '-created_at')