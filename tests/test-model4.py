# -*- coding:utf-8 -*-
import django
from django.conf import settings
from django.test.utils import get_runner
from django.test import TestCase


"""
TestCase.setUpTestData() is sometimes helpful.
"""


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        __name__,
    ]
)
django.setup()


class Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User
        for i in range(100):
            User.objects.create_superuser("admin{}".format(i), "myemail{}@example.com".format(i), '')

    def test_query(self):
        from django.contrib.auth.models import User
        with self.assertNumQueries(1):
            actual = User.objects.filter(username__startswith="admin1").count()
            self.assertEqual(actual, 11)

    def test_query1(self):
        from django.contrib.auth.models import User
        with self.assertNumQueries(1):
            actual = User.objects.filter(username__startswith="admin1").count()
            self.assertEqual(actual, 11)

    def test_query2(self):
        from django.contrib.auth.models import User
        with self.assertNumQueries(1):
            actual = User.objects.filter(username__startswith="admin1").count()
            self.assertEqual(actual, 11)


if __name__ == "__main__":
    from django.apps import apps
    for config in apps.get_app_configs():
        config.models_module = __name__
    factory = get_runner(settings)
    test_runner = factory()
    status = test_runner.run_tests([__name__])
