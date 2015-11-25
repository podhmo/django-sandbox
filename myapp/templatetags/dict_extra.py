from django import template

# add filter
register = template.Library()


@register.filter(is_safe=True)
def dict_excluded(d, exclude_key):
    return {k: v for k, v in d.items() if k != exclude_key}
