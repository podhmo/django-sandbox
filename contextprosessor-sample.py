# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)


def random_number(request):
    import random
    return {"random": random.random()}


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    settings.TEMPLATE_CONTEXT_PROCESSORS += ("{}.random_number".format(__name__), )
    django.setup()

    # use
    from django.template import RequestContext, Template
    from django.test.client import RequestFactory

    template = Template("hey, random number is {{random}}")

    request = RequestFactory().get("/")
    context = RequestContext(request)
    print(template.render(context))
    # hey, random number is 0.3016108869163481
