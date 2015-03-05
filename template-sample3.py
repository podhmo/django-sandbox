# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django import template

"""
checking enable to "in" operator in django template. => ok
"""

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    L = [1, 2, 3]

    t = template.Template("""
{%if 1 in L %}
    hello
{% endif %}
    """)
    c = template.Context({"L": L})
    print(t.render(c))
