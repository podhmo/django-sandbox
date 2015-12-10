# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django import template

"""
checking unpacking tuple in forloop
"""

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    L = [(1, 1), (2, 4), (3, 9)]

    t = template.Template("""
{%for x, y in L %}
    {{x}} * {{x}} = {{y}}
{% endfor %}
    """)
    c = template.Context({"L": L})
    print(t.render(c))
