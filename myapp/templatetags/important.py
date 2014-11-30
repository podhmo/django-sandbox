from django import template
from django.template.defaultfilters import stringfilter

# add filter
register = template.Library()


@register.filter
@stringfilter
def important(value):
    return value.upper() + "!!!!!!!"
