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
class X(models.Model):

    class Meta:
        app_label = __name__


class Y(models.Model):
    xs = models.ManyToManyField(X, related_name="ys")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import django
    django.setup()
    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    create_table(X)
    create_table(Y)
    from django.db import transaction
    # with transaction.atomic():
    xs = X.objects.bulk_create([X(id=1), X(id=2), X(id=3)])
    ys = Y.objects.bulk_create([Y(id=1), Y(id=2), Y(id=3)])
    xs[0].ys.add(ys[0])
    xs[0].ys.add(ys[1])
    xs[1].ys.add(ys[1])
    xs[2].ys.add(ys[2])

    print(xs[0].ys.all())
    print(ys[0].xs.all()) # error?
    #     transaction.set_rollback(True)
    # assert X.objects.count() == 0
