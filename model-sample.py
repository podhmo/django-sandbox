# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.db import models

"""hmm"""
from django.conf import settings
settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)
import django
from django.db import connections
from django.core.management.color import no_style
django.setup()


def create_table(model):
    connection = connections['default']
    if hasattr(connection, "schema_editor"):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)
    else:
        cursor = connection.cursor()
        sql, references = connection.creation.sql_create_model(model, no_style())
        for statement in sql:
            cursor.execute(statement)

        for f in model._meta.many_to_many:
            create_table(f.rel.through)


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
    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    create_table(Person)

    # model save
    Person(name="foo").save()

    # model query
    if Person.objects.filter(name="foo").exists():
        ob, exists = Person.objects.filter(name="foo").get_or_create()
        print(ob, exists)
