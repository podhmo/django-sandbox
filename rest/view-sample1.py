# -*- coding:utf-8 -*-
from shortcut import App  # shorthand
from shortcut import do_get, do_post, do_delete

app = App()
app.setup(apps=[__name__], root_urlconf=__name__)

# models
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'is_staff')


# viewsets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
    do_post(client, msg, "/users/", {"username": "foo"})
    msg = "create user (name=bar)"
    do_post(client, msg, "/users/", {"username": "bar"})

    msg = "listing"
    do_get(client, msg, "/users/")

    msg = "show information for user(id=1)"
    do_get(client, msg, "/users/1/")

    msg = "delete user(id=1)"
    do_delete(client, msg, "/users/1/")

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
