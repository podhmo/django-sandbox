# -*- coding:utf-8 -*-
import django
from django.conf import settings
from django.test.utils import get_runner
from django.test import TestCase
from django.db import models


"""
If you want to check N+1 query, then, assertNumQueries is helpful, maybe.
"""

settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__],
)


class Group(models.Model):
    name = models.CharField(max_length=255, default="", blank=False)

    class Meta:
        app_label = __name__


class User(models.Model):
    name = models.CharField(max_length=255, default="", blank=False)
    age = models.IntegerField(default=0, blank=False)
    group = models.ForeignKey(Group)

    class Meta:
        app_label = __name__


class Test(TestCase):
    def test_it(self):
        with self.assertNumQueries(3):
            Group(name="foo").save()
            self.assertEqual(Group.objects.count(), 1)

if __name__ == "__main__":
    django.setup()
    from django.apps import apps
    for config in apps.get_app_configs():
        config.models_module = __name__
    factory = get_runner(settings)
    test_runner = factory()
    status = test_runner.run_tests([__name__])
