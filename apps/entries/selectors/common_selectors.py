def get_entries_selector(model_class, *, start_date=None, end_date=None, shift=None, lot_number=None):
    """
    Hàm truy vấn tổng quát cho mọi loại Line sản xuất.
    model_class: Truyền vào MetalInput, BaggingInput, v.v.
    """
    queryset = model_class.objects.all()

    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])

    if shift and shift != "All":
        queryset = queryset.filter(shift=shift)

    if lot_number:
        queryset = queryset.filter(lot_number__icontains=lot_number)

    return queryset.order_by('-date', '-created_at')
