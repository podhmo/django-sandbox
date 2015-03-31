# -*- coding:utf-8 -*-
import django
from django.db import models
from django.conf import settings
from django.db import connections
from django.core.management.color import no_style
from django.forms import ModelForm, formset_factory

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


class XForm(ModelForm):
    class Meta:
        model = X

XFormSet = formset_factory(XForm)


if __name__ == "__main__":
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    django.setup()
    create_table(X)
    input_data = {}
    formset = XFormSet(input_data)
    print(formset.is_valid())
    # django.core.exceptions.ValidationError: ['ManagementForm data is missing or has been tampered with']
