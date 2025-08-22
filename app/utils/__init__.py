def to_fixed_str(value, decimals=6):
    """Convert a number to a fixed decimal string representation"""
    if value is None:
        return None
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)
