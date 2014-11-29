# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.db import models

"""hmm"""
from django.conf import settings
settings.configure(
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)


def get_connection():
    "get default database connection"
    from django.db import connections
    connection = connections['default']
    return connection


def get_cursor(connection):
    "get database cursor from connection"
    return connection.cursor()


def get_style():
    from django.core.management.color import no_style
    return no_style()


def create_tables(model):
    connection = get_connection()
    cursor = get_cursor(connection)
    style = get_style()

    sql, references = connection.creation.sql_create_model(
        model, style)
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_tables(f.rel.through)


# model definition
class Person(models.Model):
    name = models.CharField(max_length=255, null=False, default="")
    age = models.IntegerField(null=True)
    birth = models.DateTimeField(null=True)
    death = models.DateTimeField(null=True)

    class Meta:
        app_label = "myapp"


if __name__ == "__main__":
    import django
    django.setup()
    create_tables(Person)

    # model save
    Person(name="foo").save()

    # model query
    if Person.objects.filter(name="foo").exists():
        ob, exists = Person.objects.filter(name="foo").get_or_create()
        print(ob, exists)
