# -*- coding:utf-8 -*-

"""
prefetch related with self defined many to many
"""
import django
import contextlib
from django.db import models
from django.conf import settings
from django.db import connections
from django.db.models import Count


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__, "django.contrib.contenttypes"]
)
django.setup()


def create_table(model):
    connection = connections['default']
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


@contextlib.contextmanager
def with_clear_connection(c, message):
    print("\n========================================")
    print(message)
    print("========================================")
    c.queries_log.clear()
    yield


class X(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "x"
        app_label = __name__


class Y(models.Model):
    xs = models.ManyToManyField(X, related_name="ys")
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "y"
        app_label = __name__


class XX(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "xx"
        app_label = __name__


class XXtoYY(models.Model):
    xx = models.ForeignKey('XX', on_delete=models.CASCADE)
    yy = models.ForeignKey('YY', on_delete=models.CASCADE)

    class Meta:
        db_table = "xx_to_yy"
        app_label = __name__


class YY(models.Model):
    xxs = models.ManyToManyField(XX, related_name="yys", through=XXtoYY)
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "yy"
        app_label = __name__


if __name__ == "__main__":
    create_table(X)
    create_table(Y)
    create_table(XX)
    create_table(YY)
    create_table(XXtoYY)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    X.objects.bulk_create([
        X(name="x0"),
        X(name="x1"),
        X(name="x2")
    ])
    xs = list(X.objects.all())
    Y.objects.bulk_create([
        Y(name="y0"),
        Y(name="y1"),
        Y(name="y2")
    ])
    ys = list(Y.objects.all())
    xs[0].ys.add(ys[0])
    xs[0].ys.add(ys[1])
    xs[0].ys.add(ys[2])
    xs[1].ys.add(ys[1])
    xs[1].ys.add(ys[2])
    xs[2].ys.add(ys[2])

    XX.objects.bulk_create([
        XX(name="xx0"),
        XX(name="xx1"),
        XX(name="xx2")
    ])
    xxs = list(XX.objects.all())
    YY.objects.bulk_create([
        YY(name="yy0"),
        YY(name="yy1"),
        YY(name="yy2")
    ])
    yys = list(YY.objects.all())
    XXtoYY.objects.create(xx=xxs[0], yy=yys[0])
    XXtoYY.objects.create(xx=xxs[0], yy=yys[1])
    XXtoYY.objects.create(xx=xxs[0], yy=yys[2])
    XXtoYY.objects.create(xx=xxs[1], yy=yys[1])
    XXtoYY.objects.create(xx=xxs[1], yy=yys[2])
    XXtoYY.objects.create(xx=xxs[2], yy=yys[2])

    c = connections["default"]
    with with_clear_connection(c, "no prefetch"):
        r = []
        for x in X.objects.all():
            r.append((x.name, [y.name for y in x.ys.all()]))
        print("\n".join(map(str, r)))

    with with_clear_connection(c, "prefetch"):
        r = []
        for x in X.objects.all().prefetch_related("ys"):
            r.append((x.name, [y.name for y in x.ys.all()]))
        print("\n".join(map(str, r)))

    with with_clear_connection(c, "no prefetch (self defined)"):
        r = []
        for xx in XX.objects.all():
            r.append((xx.name, [yy.name for yy in xx.yys.all()]))
        print("\n".join(map(str, r)))

    with with_clear_connection(c, "prefetch (self defined)"):
        r = []
        for xx in XX.objects.all().prefetch_related("yys"):
            r.append((xx.name, [yy.name for yy in xx.yys.all()]))
        print("\n".join(map(str, r)))
