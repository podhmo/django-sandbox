# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django.conf import settings
import os.path
import rest_framework


settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    INSTALLED_APPS=[
        'django.contrib.staticfiles',
        "rest_framework",
        __name__,
    ],
    STATIC_URL='/static/',
    STATIC_ROOT=os.path.abspath(os.path.join(rest_framework.__path__[0], 'static')),
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
    ),
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASS": [
            "rest_framework.permissions.AllowAny"
        ]
    },
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)


# model
from django.db import connections
from django.core.management.color import no_style


def create_table(model):
    connection = connections['default']
    cursor = connection.cursor()
    sql, references = connection.creation.sql_create_model(model, no_style())
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)

# rest
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


# url
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
urlpatterns += staticfiles_urlpatterns()


def main_client():
    """call view via Client"""
    from django.test.client import Client
    client = Client()

    # success request
    response = client.get("/users/")
    print("status code: {response.status_code}".format(response=response))
    print("response content: {response.content}".format(response=response))

    response = client.post("/users/", {"username": "foo"})
    print("status code: {response.status_code}".format(response=response))
    print("response content: {response.content}".format(response=response))

    response = client.get("/users/1/?format=json")
    print("status code: {response.status_code}".format(response=response))
    print("response content: {response.content}".format(response=response))


def main_run_server():
    """runserver localhost:8000"""
    from django.core.management.commands.runserver import Command
    Command().execute()

if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-server", dest="run_server", action="store_true", default=False)
    args = parser.parse_args(sys.argv[1:])

    import django
    django.setup()
    create_table(User)

    if args.run_server:
        main_run_server()
    else:
        main_client()
