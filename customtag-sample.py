# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django import template

"""
see also: myapp/templatetags/important.py
"""

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    settings.INSTALLED_APPS += ("myapp", )
    django.setup()

    t = template.Template("""\
    {% load important %}
    hello {{something|important}}.""")
    c = template.Context({"something": "world"})
    print(t.render(c))
