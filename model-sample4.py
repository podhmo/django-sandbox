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


class X(models.Model):

    class Meta:
        app_label = __name__


class Y(models.Model):
    xs = models.ManyToManyField(X, related_name="ys")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    # # this is also ok #
    # from django.conf import settings
    # settings.INSTALLED_APPS += (__name__, )
    # django.setup()

    from django.apps import apps
    apps.populate([__name__])

    create_table(X)
    create_table(Y)

    xs = X.objects.bulk_create([X(id=1), X(id=2), X(id=3)])
    ys = Y.objects.bulk_create([Y(id=1), Y(id=2), Y(id=3)])
    xs[0].ys.add(ys[0])
    xs[0].ys.add(ys[1])
    xs[1].ys.add(ys[1])
    xs[2].ys.add(ys[2])

    print(xs[0].ys.all())
    print(ys[0].xs.all())  # error?
