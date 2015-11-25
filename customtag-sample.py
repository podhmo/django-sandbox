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
    settings.configure(INSTALLED_APPS=["myapp"])
    django.setup()

    t = template.Template("""\
    {% load important %}
    {% load currenttime %}
    hello {{something|important}}. current time is {% current_time "%Y-%m-%dT%H:%M:%SZ" %}""")
    c = template.Context({"something": "world"})
    print(t.render(c))

    # hello WORLD!!!!!!!. current time is 2014-11-30T10:28:25Z
