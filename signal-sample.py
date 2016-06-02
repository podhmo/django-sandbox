# -*- coding:utf-8 -*-

"""
proxy=True object also signal is activated?
"""
import django
from django.db import models
from django.conf import settings
from django.db import connections
from django.db.models import signals

settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__]
)
django.setup()


def create_table(model):
    connection = connections['default']
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class Person(models.Model):
    name = models.CharField(max_length=32, default="a", blank=False)
    ctime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__


class Worker(Person):
    class Meta:
        proxy = True
        app_label = __name__


def hai(sender, instance, **kwargs):
    print("----------------------------------------")
    print("hai", sender, instance, kwargs)
    print("----------------------------------------")

signals.pre_save.connect(hai, sender=Person)

if __name__ == "__main__":
    create_table(Person)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    person = Person(name="foo")
    person.save()

    worker = Worker(name="bar")
    worker.save()
