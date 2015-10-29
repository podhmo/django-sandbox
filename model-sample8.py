# -*- coding:utf-8 -*-

"""
remove default order
"""

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


class Item(models.Model):
    name = models.CharField(max_length=255, default="foo", blank=True)
    grade = models.CharField(max_length=1, default="a", choices=(("a", "good"), ("b", "so-so"), ("c", "bad")))

    class Meta:
        app_label = __name__
        ordering = ["name"]  # default ordering settings

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    django.setup()

    create_table(Item)

    print(Item.objects.all().query)  # select with ORDER BY clause

    qs = Item.objects.all()
    qs.query.clear_ordering(True)  # remove ORDER BY clause
    print(qs.query)
