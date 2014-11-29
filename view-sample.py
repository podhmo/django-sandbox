# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django.http import HttpResponse


# view
def hello_view(request):
    from django.core.urlresolvers import reverse
    print("this is {}".format(reverse("hello")))
    return HttpResponse("ok")


# url definition
from django.conf.urls import patterns, url

urlpatterns = patterns(
    "",
    url("^hello/$", hello_view, name="hello")
)


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure(
        ROOT_URLCONF=__name__,  # xxx:
        ALLOWED_HOSTS=['*']
    )
    django.setup()

    # call view via Client
    from django.test.client import Client

    client = Client()

    # redirect
    assert client.get("/hello").status_code == 301

    # success request
    response = client.get("/hello/")

    print("status code: {response.status_code}".format(response=response))
    print("response content: {response.content}".format(response=response))
