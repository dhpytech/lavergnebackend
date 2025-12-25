# """ Format Number
#     EN: Chuẩn Anh Mỹ
#     VN: Chuẩn Việt Nam
# """
def format_number(num, style="EN"):
    s = f"{num:,.2f}"
    if style.upper() == "VN":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s
