"""Normalize complete Iranian mobile numbers without truncating their identity."""

_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_phone(value: str) -> str:
    digits = value.translate(_TRANSLATION)
    if len(digits) == 9:
        digits = f"09{digits}"
    if len(digits) != 11 or not digits.startswith("09") or not all("0" <= ch <= "9" for ch in digits):
        raise ValueError("phone must be an Iranian mobile number")
    return digits
