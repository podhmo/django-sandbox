# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django import template

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    t = template.Template("hello {{something}}.")
    c = template.Context({"something": "world"})
    print(t.render(c))
