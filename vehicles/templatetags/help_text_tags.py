"""
Template tags for contextual help texts.
"""

from django import template

from vehicles.help_texts import get_help_text, get_progress_steps, get_required_documents

register = template.Library()


@register.simple_tag
def help_tooltip(field_name, language="fr"):
    """
    Returns the short help text for a field to be used in tooltips.

    Usage: {% help_tooltip 'plaque_immatriculation' 'fr' %}
    """
    help_text = get_help_text(field_name, language, detailed=False)
    return help_text if help_text else ""


@register.simple_tag
def help_detailed(field_name, language="fr"):
    """
    Returns the detailed help text for a field.

    Usage: {% help_detailed 'plaque_immatriculation' 'fr' %}
    """
    help_text = get_help_text(field_name, language, detailed=True)
    return help_text if help_text else {}


@register.simple_tag
def required_docs(vehicle_category, language="fr"):
    """
    Returns the list of required documents for a vehicle category.

    Usage: {% required_docs 'AERIEN' 'fr' %}
    """
    return get_required_documents(vehicle_category, language)


@register.simple_tag
def progress_steps(language="fr"):
    """
    Returns the progress steps.

    Usage: {% progress_steps 'fr' %}
    """
    return get_progress_steps(language)


@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary.

    Usage: {{ my_dict|get_item:'key' }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
