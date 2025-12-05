from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def format_ariary(value):
    """
    Format a number as Ariary currency with thousand separators using spaces.
    Malagasy Ariary does not use decimals - always rounds to integer.
    Example: 100000 -> "100 000 Ar"
    """
    if value is None:
        return "0 Ar"

    try:
        # Convert to Decimal for precise handling, then round to integer
        if isinstance(value, str):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))

        # Round to nearest integer (Ariary has no decimal)
        integer_value = int(value.quantize(Decimal("1")))

        # Convert to string for formatting
        value_str = str(abs(integer_value))

        # Add thousand separators with spaces
        # Reverse the string, add spaces every 3 digits, then reverse back
        reversed_int = value_str[::-1]
        spaced = " ".join([reversed_int[i : i + 3] for i in range(0, len(reversed_int), 3)])
        formatted_int = spaced[::-1]

        # Add negative sign if needed
        if integer_value < 0:
            formatted_int = f"-{formatted_int}"

        return f"{formatted_int} Ar"

    except (ValueError, TypeError, InvalidOperation):
        # Fallback to "0 Ar" when value cannot be parsed
        return "0 Ar"


@register.filter
def format_number_spaces(value):
    """
    Format a number with thousand separators using spaces.
    Rounds to integer for Ariary (no decimals).
    Example: 100000 -> "100 000"
    """
    if value is None:
        return "0"

    try:
        # Convert to integer (round if needed)
        if isinstance(value, (int, float, Decimal)):
            integer_value = int(round(float(value)))
        else:
            integer_value = int(round(float(str(value))))

        # Convert to string for formatting
        value_str = str(abs(integer_value))

        # Add thousand separators with spaces
        reversed_int = value_str[::-1]
        spaced = " ".join([reversed_int[i : i + 3] for i in range(0, len(reversed_int), 3)])
        formatted_int = spaced[::-1]

        # Add negative sign if needed
        if integer_value < 0:
            formatted_int = f"-{formatted_int}"

        return formatted_int

    except (ValueError, TypeError):
        return str(value)


@register.filter
def format_currency(value):
    """
    Alias for format_ariary - formats a number as Ariary currency.
    Example: 100000 -> "100 000 Ar"
    """
    return format_ariary(value)
