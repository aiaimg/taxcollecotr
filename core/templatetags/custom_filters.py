"""
Custom template filters for the Tax Collector application
"""

from django import template

register = template.Library()


@register.filter(name="abs")
def absolute_value(value):
    """
    Returns the absolute value of a number
    Usage: {{ value|abs }}
    """
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value


@register.filter(name="multiply")
def multiply(value, arg):
    """
    Multiplies the value by the argument
    Usage: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value


@register.filter(name="divide")
def divide(value, arg):
    """
    Divides the value by the argument
    Usage: {{ value|divide:2 }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value


@register.filter(name="percentage")
def percentage(value, total):
    """
    Calculates percentage of value relative to total
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name="format_ariary")
def format_ariary(value):
    """
    Formats a number as Ariary currency
    Usage: {{ value|format_ariary }}
    """
    try:
        return f"{int(value):,} Ar".replace(",", " ")
    except (ValueError, TypeError):
        return value


@register.filter(name="get_item")
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except Exception:
        return ""
