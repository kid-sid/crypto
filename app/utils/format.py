from decimal import Decimal, ROUND_HALF_UP


def to_fixed_str(value: float | None, decimals: int = 8) -> str | None:
    """Convert float/scientific notation to fixed decimal string."""
    if value is None:
        return None
    q = Decimal('1.' + '0' * decimals)  # quantization step
    return str(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))

def format_to_millions(value: float | int) -> str:
    """
    Convert a large number into millions with 2 decimal places.
    Example: 123456789 -> "123.46M"
    """
    if value is None:
        return None
    return f"{value / 1_000_000:.2f}M"