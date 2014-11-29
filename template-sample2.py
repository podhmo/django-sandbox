# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.template.loader import render_to_string

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure(
        TEMPLATE_LOADERS=('django.template.loaders.filesystem.Loader',),
        TEMPLATE_DIRS = (".",),
    )
    django.setup()

    print(render_to_string("./hello.html", {"something": "world"}))
