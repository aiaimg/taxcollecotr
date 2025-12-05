import re

from django import template

register = template.Library()


@register.filter(name="mul")
def mul(value, arg):
    """Multiply two numeric values, safely handling strings and None."""
    try:
        if value is None or arg is None:
            return 0
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name="add_class")
def add_class(bound_field, css_class):
    """Append a CSS class to a form field's widget attrs and return the field."""
    try:
        widget = bound_field.field.widget
        existing = widget.attrs.get("class", "").strip()
        widget.attrs["class"] = (existing + " " + str(css_class)).strip()
        return bound_field
    except Exception:
        return bound_field


@register.filter(name="attr")
def attr(bound_field, arg):
    """Set a single attribute (key:value) on a form field's widget and return the field."""
    try:
        key, value = str(arg).split(":", 1)
        bound_field.field.widget.attrs[key.strip()] = value.strip()
        return bound_field
    except Exception:
        return bound_field


@register.filter(name="format_plate")
def format_plate(plate):
    """Format vehicle plate number with space for display (e.g., 1234TAA -> 1234 TAA)"""
    if not plate:
        return plate

    # Don't format temporary plates
    if plate.startswith("TEMP-"):
        return plate

    # Format: 1234TAA -> 1234 TAA (add space before letters)
    match = re.match(r"^(\d+)([A-Z]+)$", plate)
    if match:
        return f"{match.group(1)} {match.group(2)}"

    return plate
