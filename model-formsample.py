# -*- coding:utf-8 -*-
import logging
from django.forms.models import ModelForm
from django.db import models
from django.conf import settings
from django.db import connections
from django.core.management.color import no_style
logger = logging.getLogger(__name__)
"""hmm"""

settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)


def create_table(model):
    connection = connections['default']
    cursor = connection.cursor()
    sql, references = connection.creation.sql_create_model(model, no_style())
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)


# model definition
class Point(models.Model):
    value = models.IntegerField(default=0)

    class Meta:
        app_label = "myapp"


class PointForm(ModelForm):

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
    print(PointForm().fields)
    print(PointForm()["value"])
    # <input id="id_value" name="value" type="number" value="0" />

    form = PointForm({"value": "0"})
    print(form.is_valid())
    print(form.cleaned_data)
