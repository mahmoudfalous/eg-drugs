"""
Barcode validation (GS1 / EAN-13) for the Egyptian Drug Database.

GS1 Check Digit algorithm for EAN-13:
- From left to right, digits at odd positions (1st, 3rd, ...) are multiplied by 1
- Digits at even positions (2nd, 4th, ...) are multiplied by 3
- Sum the results, check digit = (10 - (sum % 10)) % 10
- If the check digit matches the last barcode digit, the barcode is valid
"""

from typing import Tuple


def gs1_check_digit(digits_without_check: str) -> int:
    """Calculate GS1 check digit for a digit string (without the last check digit)."""
    total = 0
    for i, ch in enumerate(digits_without_check):
        d = int(ch)
        # From left: even positions (0-indexed) multiply by 1, odd by 3
        multiplier = 1 if i % 2 == 0 else 3
        total += d * multiplier
    return (10 - (total % 10)) % 10


def validate_ean13(barcode: str) -> Tuple[bool, str]:
    """
    Validate an EAN-13 barcode.
    Returns (is_valid, message).
    """
    if not barcode or not barcode.isdigit():
        return False, "Barcode is empty or contains invalid digits"

    if len(barcode) != 13:
        return False, f"Barcode length is {len(barcode)} digits, 13 required"

    body = barcode[:12]
    check_digit = int(barcode[12])
    expected = gs1_check_digit(body)

    if check_digit == expected:
        return True, "Barcode is valid"
    return False, f"Check digit incorrect (expected: {expected}, found: {check_digit})"


def validate_barcode_any(barcode: str) -> Tuple[bool, str]:
    """
    Validate any barcode. If length is 13, apply GS1/EAN-13;
    otherwise just check that it is numeric and non-empty.
    """
    if not barcode or not barcode.strip():
        return False, "Barcode is empty"
    barcode = barcode.strip()
    if not barcode.isdigit():
        return False, "Barcode contains non-digit characters"
    if len(barcode) == 13:
        return validate_ean13(barcode)
    return True, f"Numeric barcode of length {len(barcode)} (GS1 not applied for non-13 length)"
