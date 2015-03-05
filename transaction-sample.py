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


def create_table(model):
    connection = get_connection()
    cursor = get_cursor(connection)
    style = get_style()

    sql, references = connection.creation.sql_create_model(
        model, style)
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

    from django.db import transaction
    # atomic simply
    try:
        with transaction.atomic():
            Person(name="foo").save()
            raise Exception("oops")
    except:
        assert Person.objects.count() == 0

    # manual transaction
    try:
        transaction.set_autocommit(False)
        assert Person.objects.count() == 0
        Person(name="boo").save()
        transaction.rollback()
        assert Person.objects.count() == 0
        raise Exception("oops")
    except:
        pass
    finally:
        transaction.set_autocommit(True)
        assert Person.objects.count() == 0

    # comprex situation
    with transaction.atomic():
        Person(name="a").save()
        assert Person.objects.count() == 1
        try:
            with transaction.atomic():
                Person(name="b").save()
                assert Person.objects.count() == 2
                raise Exception("oops")
        except:
            assert Person.objects.count() == 1
    assert Person.objects.count() == 1

