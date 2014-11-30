# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)


def random_number(request):
    import random
    return {"random": random.random()}


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure(TEMPLATE_DIRS=("./templates",))
    settings.TEMPLATE_CONTEXT_PROCESSORS += ("{}.random_number".format(__name__), )
    django.setup()

    # use
    from django.shortcuts import render
    from django.test.client import RequestFactory

    request = RequestFactory().get("/")
    response = render(request, "with_random.html", {})

    print(response.content)
    # b'hey, random number is 0.42478061489323593\n'
