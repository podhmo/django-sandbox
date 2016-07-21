# -*- coding:utf-8 -*-
"""
with pagination
"""

from shortcut import App  # shorthand
from shortcut import do_get, do_post

app = App()
app.setup(apps=[__name__], root_urlconf=__name__)

# models
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'is_staff')


# pagination
from rest_framework import pagination


class MyPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10000


# viewsets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPagination


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns = app.setup_urlconf(router)


def main_client(client):
    """call view via Client"""
    # success request
    msg = "listing (empty)"
    do_get(client, msg, "/users/")

    msg = "create user (name=foo)"
    for i in range(10):
        do_post(client, msg, "/users/", {"username": "foo{}".format(i)})

    msg = "listing"
    do_get(client, msg, "/users/")


if __name__ == "__main__":
    app.create_table(User)
    parser = app.create_arg_parser()
    args = parser.parse_args()

    if args.run_server:
        app.run_server(port=8080)
    else:
        app.run_client(main_client)
