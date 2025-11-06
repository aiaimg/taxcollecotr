from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_ariary(value):
    """
    Format a number as Ariary currency with thousand separators using spaces.
    Example: 100000 -> "100 000 Ar"
    """
    if value is None:
        return "0 Ar"
    
    try:
        # Convert to Decimal for precise handling
        if isinstance(value, str):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Format with 2 decimal places
        formatted = f"{value:.2f}"
        
        # Split into integer and decimal parts
        if '.' in formatted:
            integer_part, decimal_part = formatted.split('.')
        else:
            integer_part, decimal_part = formatted, "00"
        
        # Add thousand separators with spaces
        # Reverse the string, add spaces every 3 digits, then reverse back
        reversed_int = integer_part[::-1]
        spaced = ' '.join([reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)])
        formatted_int = spaced[::-1]
        
        # Remove trailing zeros from decimal part
        decimal_part = decimal_part.rstrip('0').rstrip('.')
        
        if decimal_part:
            return f"{formatted_int}.{decimal_part} Ar"
        else:
            return f"{formatted_int} Ar"
            
    except (ValueError, TypeError):
        return f"{value} Ar"

@register.filter
def format_number_spaces(value):
    """
    Format a number with thousand separators using spaces.
    Example: 100000 -> "100 000"
    """
    if value is None:
        return "0"
    
    try:
        # Convert to string and handle decimal numbers
        if isinstance(value, (int, float)):
            value_str = str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)
        else:
            value_str = str(value)
        
        # Split into integer and decimal parts if needed
        if '.' in value_str:
            integer_part, decimal_part = value_str.split('.')
        else:
            integer_part, decimal_part = value_str, None
        
        # Add thousand separators with spaces
        reversed_int = integer_part[::-1]
        spaced = ' '.join([reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)])
        formatted_int = spaced[::-1]
        
        if decimal_part:
            return f"{formatted_int}.{decimal_part}"
        else:
            return formatted_int
            
    except (ValueError, TypeError):
        return str(value)