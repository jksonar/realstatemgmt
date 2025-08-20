from django import template

register = template.Library()

@register.filter
def as_currency(value):
    """Formats a number as a currency."""
    return f'${value:,.2f}'
