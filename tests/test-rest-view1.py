# -*- coding:utf-8 -*-
import logging
import os.path
from django.conf import settings
from django.conf.urls import url, include
import rest_framework

logger = logging.getLogger(__name__)



# django.contriub.**.* modules need calling `settings.configure()`, before importing it.
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # NOQA
from django.contrib.auth.models import User  # NOQA
from rest_framework.test import APITestCase  # NOQA
from rest_framework import routers, serializers, viewsets, status  # NOQA


# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
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

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
urlpatterns += staticfiles_urlpatterns()


def extract_error_message(response):
    # this is utility function, when test is failed
    return getattr(response, "data", None) or response.content


class Test(APITestCase):
    def setUp(self):
        super().setUp()
        self.login_user = User.objects.create_superuser('admin', 'myemail@test.com', '')
        self.client.force_authenticate(self.login_user)

    def test_listing(self):
        path = "/api/users/"
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=extract_error_message(response))
        self.assertEqual(len(response.data), 1, msg=response.data)

    def test_listing__with_another_user(self):
        User.objects.create_user('another', 'myemail@test.com', '')
        path = "/api/users/"
        response = self.client.get(path, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=extract_error_message(response))
        self.assertEqual(len(response.data), 2, msg=response.data)

    def test_create(self):
        self.assertEqual(User.objects.count(), 1)
        path = "/api/users/"
        data = {"username": "another", "password": "hmm", "email": "myemail+another@test.com"}
        response = self.client.post(path, format="json", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=extract_error_message(response))

        self.assertEqual(User.objects.count(), 2)

    def test_update(self):
        self.assertEqual(User.objects.count(), 1)
        path = "/api/users/{}/".format(self.login_user.id)
        data = {"username": "another"}
        response = self.client.patch(path, format="json", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=extract_error_message(response))

        self.assertEqual(User.objects.get(id=self.login_user.id).username, "another")

    def test_delete(self):
        self.assertEqual(User.objects.count(), 1)
        path = "/api/users/{}/".format(self.login_user.id)
        data = {"username": "another"}
        response = self.client.delete(path, format="json", data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=extract_error_message(response))

        self.assertEqual(User.objects.count(), 0)


if __name__ == "__main__":
    import django
    from django.apps import apps
    from django.test.utils import get_runner

    django.setup()
    for config in apps.get_app_configs():
        config.models_module = __name__
    factory = get_runner(settings)
    test_runner = factory()
    test_runner.run_tests([__name__])
