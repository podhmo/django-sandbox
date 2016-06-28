# -*- coding:utf-8 -*-
import django
from django.conf import settings
from django.test.utils import get_runner
from django.test import TestCase
from django.db import models


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__],
    LOGGING={
        "version": 1,
        "handlers": {
            "stderr": {
                "level": "DEBUG",
                "class": "logging.StreamHandler"
            }
        },
        "loggers": {
            "django": {
                "level": "DEBUG",
                "handlers": ["stderr"],
                "propagate": True,
            }
        }
    }
)
django.setup()


class Item(models.Model):
    name = models.CharField(max_length=255, default="foo", blank=True)

    class Meta:
        app_label = __name__


class Test(TestCase):
    def test_it(self):
        from django.test.utils import CaptureQueriesContext
        from django.db import connections
        with CaptureQueriesContext(connections["default"]):
            Item(name="foo").save()


if __name__ == "__main__":
    from django.apps import apps
    for config in apps.get_app_configs():
        config.models_module = __name__
    factory = get_runner(settings)
    test_runner = factory()
    status = test_runner.run_tests([__name__])
