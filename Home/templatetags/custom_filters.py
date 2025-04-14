from django import template
from babel.numbers import format_decimal

register = template.Library()

@register.filter
def babel_decimal(value, locale='fa_IR'):
    try:
        return format_decimal(value, locale=locale)
    except Exception:
        return value