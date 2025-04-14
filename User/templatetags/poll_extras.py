from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """فیلتر ضرب دو عدد"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0