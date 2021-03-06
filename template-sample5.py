# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.template.loader import render_to_string

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure(
        TEMPLATE_LOADERS=('django.template.loaders.filesystem.Loader',),
        TEMPLATE_DIRS = ("./templates",),
        INSTALLED_APPS = (__name__, "myapp")
    )
    django.setup()

    print(render_to_string("./with_data.html", {"something": "world"}))
