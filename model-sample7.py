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


class X(models.Model):
    name = models.CharField(max_length=255, default="foo", blank=True)
    grade = models.CharField(max_length=1, default="a", choices=(("a", "good"), ("b", "so-so"), ("c", "bad")))

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    django.setup()
    create_table(X)

    x = X(name="foo", grade="c")
    x.save()
    x.name = "boo"
    x.refresh_from_db()
    assert x.name == "foo"
    assert x.grade == "c"
    assert x.get_grade_display() == "bad"
