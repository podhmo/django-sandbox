# -*- coding:utf-8 -*-
import django
from django.db import models
from django.conf import settings
from django.db import connections
from django.core.management.color import no_style


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__]
)


def create_table(model):
    connection = connections['default']
    cursor = connection.cursor()
    sql, references = connection.creation.sql_create_model(model, no_style())
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)


class X(models.Model):
    name = models.CharField(max_length=255, default="foo", blank=True)

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    django.setup()
    create_table(X)

    xs = X.objects.bulk_create([X(id=1), X(id=2), X(id=3)])

    print(X.objects.count())
