# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
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
class Point(models.Model):
    value = models.IntegerField(default=0)

    class Meta:
        app_label = "myapp"


from django.forms.models import ModelForm


class PointForm(ModelForm):
    pass

    class Meta:
        model = Point

if __name__ == "__main__":
    import django
    django.setup()
    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    create_table(Point)
    print(PointForm()["value"])
    # <input id="id_value" name="value" type="number" value="0" />

    form = PointForm({"value": "0"})
    print(form.is_valid())
    print(form.cleaned_data)