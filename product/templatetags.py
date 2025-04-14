from django import template
import jdatetime

register = template.Library()

@register.filter
def jformat(value, date_format):
    if value:
        return jdatetime.date.fromgregorian(date=value).strftime(date_format)
    return ''