# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.db import models

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
import datetime


class HasDate(models.Model):
    date = models.DateField(null=False, default=datetime.date.today)
    datetime = models.DateTimeField(null=False, default=datetime.datetime.now)

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

    create_table(HasDate)

    # model save
    HasDate().save()
    from django.db import connection
    cursor = connection.cursor()

    print("----------------------------------------")
    cursor.execute("select * from myapp_hasdate;")
    for row in cursor.fetchall():
        print(row)

    print("----------------------------------------")
    cursor.execute("select A.* from (select * from myapp_hasdate) A;")
    for row in cursor.fetchall():
        print(row)

    print("----------------------------------------")
    cursor.execute("select A.*, B.* from myapp_hasdate A join myapp_hasdate B on A.id = B.id")
    for row in cursor.fetchall():
        print(row)

