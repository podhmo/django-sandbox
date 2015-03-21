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


class Y(models.Model):
    name = models.CharField(max_length=255, default="foo", blank=True)

    class Meta:
        app_label = __name__


class XorY(models.Model):
    x_id = models.IntegerField(null=True)
    y_id = models.IntegerField(null=True)

    class Meta:
        app_label = __name__
        managed = False

    def convert(self):
        if self.x_id != -1:
            return X(id=self.x_id)
        else:
            return Y(id=self.y_id)


def create_view():
    connection = connections['default']
    cursor = connection.cursor()
    sql = """\
create view {prefix}_xory as
  select id as x_id,
         -1 as y_id,
         -1 as id
  from {prefix}_x
  union all
  select -1 as x_id,
         id as y_id,
         -1 as id
  from {prefix}_y
""".format(prefix=__name__)
    cursor.execute(sql)
    cursor.fetchall()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    django.setup()

    create_table(X)
    create_table(Y)
    create_view()

    xs = X.objects.bulk_create([X(id=1), X(id=2), X(id=3)])
    ys = Y.objects.bulk_create([Y(id=1), Y(id=2), Y(id=3)])

    print(X.objects.count())
    for x_or_y in XorY.objects.all():
        instance = x_or_y.convert()
        instance.name = "bar"
        instance.save()
    print(X.objects.count())
