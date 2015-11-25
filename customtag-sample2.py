# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django import template

"""
see also: myapp/templatetags/dict_extra.py
"""

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    settings.INSTALLED_APPS += ("myapp", )
    django.setup()

    t = template.Template("""\
    {% load dict_extra %}
    {{ob|dict_excluded:"last_name"|dict_excluded:"first_name"|safe}}
    """)
    c = template.Context({"ob": {"first_name": "foo", "age": 20, "last_name": "bar"}})
    print(t.render(c))
