import re

from django.core.exceptions import ValidationError


def normalize_phone(raw):
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("855"):
        digits = "0" + digits[3:]
    if not 8 <= len(digits) <= 11:
        raise ValidationError("Please enter a valid phone number.")
    return digits
