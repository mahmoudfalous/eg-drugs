"""
تحقق من صحة الباركود (GS1 / EAN-13) لقاعدة بيانات الأدوية المصرية.

خوارزمية GS1 Check Digit لـ EAN-13:
- من اليسار إلى اليمين، الأرقام في المواقع الفردية (الرقم الأول، الثالث، ...) تُضرب بـ 1
- الأرقام في المواقع الزوجية (الثاني، الرابع، ...) تُضرب بـ 3
- يُجمع الناتج، ورقم التحقق = (10 - (المجموع % 10)) % 10
- إذا تطابق رقم التحقق مع آخر رقم في الباركود → الباركود صالح
"""

from typing import Tuple


def gs1_check_digit(digits_without_check: str) -> int:
    """حساب رقم التحقق GS1 لسلسلة أرقام (بدون رقم التحقق الأخير)."""
    total = 0
    for i, ch in enumerate(digits_without_check):
        d = int(ch)
        # من اليسار: المواقع الزوجية (0-indexed) تُضرب بـ 1، الفردية بـ 3
        multiplier = 1 if i % 2 == 0 else 3
        total += d * multiplier
    return (10 - (total % 10)) % 10


def validate_ean13(barcode: str) -> Tuple[bool, str]:
    """
    التحقق من صحة باركود EAN-13.
    يعيد (صالح، رسالة).
    """
    if not barcode or not barcode.isdigit():
        return False, "الباركود فارغ أو يحتوي على أرقام غير صالحة"

    if len(barcode) != 13:
        return False, f"طول الباركود {len(barcode)} رقم، المطلوب 13 رقماً"

    body = barcode[:12]
    check_digit = int(barcode[12])
    expected = gs1_check_digit(body)

    if check_digit == expected:
        return True, "باركود صالح"
    return False, f"رقم التحقق غير صحيح (المتوقع: {expected}، الموجود: {check_digit})"


def validate_barcode_any(barcode: str) -> Tuple[bool, str]:
    """
    التحقق من أي باركود. إذا كان طول 13 يُطبق GS1/EAN-13،
    وإلا يُفحص فقط أن يكون رقمياً وغير فارغ.
    """
    if not barcode or not barcode.strip():
        return False, "الباركود فارغ"
    barcode = barcode.strip()
    if not barcode.isdigit():
        return False, "الباركود يحتوي على حروف غير رقمية"
    if len(barcode) == 13:
        return validate_ean13(barcode)
    return True, f"باركود رقمي بطول {len(barcode)} (لم يُطبق GS1 لطول غير 13)"
