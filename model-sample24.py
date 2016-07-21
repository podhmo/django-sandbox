# -*- coding:utf-8 -*-

"""
many to many relation and unexpected join
"""
import django
import contextlib
from django.db import models
from django.db.models import Prefetch
from django.conf import settings
from django.db import connections


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


# class XQuerySet(models.QuerySet):
#     def valid_set(self):
#         return self.filter(is_valid=True).order_by("-ctime")


class X(models.Model):
    # objects = XQuerySet.as_manager()

    name = models.CharField(max_length=32, null=False, default="")
    ctime = models.DateTimeField(auto_now_add=True, null=False)
    is_valid = models.BooleanField(default=True, null=False)

    @classmethod
    def valid_set(cls, qs=None):
        if qs is None:
            qs = cls.objects.all()
        return qs.filter(is_valid=True).order_by("-ctime")

    class Meta:
        db_table = "x"
        app_label = __name__


class XTag(models.Model):
    xs = models.ManyToManyField(X, related_name="tags")
    name = models.CharField(max_length=32, null=False, default="", unique=True)

    class Meta:
        db_table = "x_tag"
        app_label = __name__


def custom_relation_property(getter):
    name = getter.__name__
    cache_name = "_{}".format(name)

    def _getter(self):
        result = getattr(self, cache_name, None)
        if result is None:
            result = getter(self)
            setattr(self, cache_name, result)
        return result

    def _setter(self, value):
        setattr(self, cache_name, value)

    prop = property(_getter, _setter, doc=_getter.__doc__)
    return prop


class Y(models.Model):
    name = models.CharField(max_length=32, null=False, default="")
    ctime = models.DateTimeField(auto_now_add=True, null=False)
    is_valid = models.BooleanField(default=True, null=False)

    xs = models.ManyToManyField(X, related_name="ys")

    @custom_relation_property
    def valid_xs(self):
        return X.valid_set(self.xs.all())

    @classmethod
    def prefetch_valid_xs(cls):
        return Prefetch("xs", queryset=X.valid_set(), to_attr="valid_xs")

    class Meta:
        db_table = "y"
        app_label = __name__


@contextlib.contextmanager
def with_clear_connection(c, message):
    print("\n========================================")
    print(message)
    print("========================================")
    c.queries_log.clear()
    yield
    print(len(c.queries_log))


if __name__ == "__main__":
    create_table(X)
    create_table(Y)
    create_table(XTag)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    X.objects.bulk_create([
        X(name="x0", is_valid=False),
        X(name="x1"),
        X(name="x2")
    ])
    Y.objects.bulk_create([
        Y(name="y0", is_valid=False),
        Y(name="y1"),
        Y(name="y2")
    ])
    xs = list(X.objects.all())
    ys = list(Y.objects.all())

    xs[0].ys.add(ys[0])
    xs[0].ys.add(ys[1])
    xs[0].ys.add(ys[2])
    xs[1].ys.add(ys[1])
    xs[1].ys.add(ys[2])
    xs[2].ys.add(ys[2])

    XTag.objects.bulk_create([
        XTag(name="a"),
        XTag(name="b"),
        XTag(name="c"),
    ])
    tags = list(XTag.objects.all())

    xs[0].tags.add(tags[0])
    xs[1].tags.add(tags[0])
    xs[2].tags.add(tags[0])
    xs[1].tags.add(tags[1])
    xs[2].tags.add(tags[1])
    xs[2].tags.add(tags[2])

    c = connections["default"]
    with with_clear_connection(c, "all"):
        for y in Y.objects.all():
            print("@@", y.id, y.name, [x.name for x in y.xs.all()])

    with with_clear_connection(c, "instance property"):
        for y in Y.objects.all():
            print("@@", y.id, y.name, [x.name for x in y.valid_xs])

    with with_clear_connection(c, "prefetch related, explicitly"):
        prefetch = Prefetch("xs", X.valid_set(X.objects.all()), "valid_xs")
        for y in Y.objects.all().prefetch_related(prefetch):
            print("@@", y.id, y.name, [x.name for x in y.valid_xs])

    with with_clear_connection(c, "prefetch related, wrapped method"):
        for y in Y.objects.all().prefetch_related(Y.prefetch_valid_xs()):
            print("@@", y.id, y.name, [x.name for x in y.valid_xs])

    with with_clear_connection(c, "more_prefetch"):
        for y in Y.objects.all().prefetch_related(Y.prefetch_valid_xs(), "valid_xs__tags"):
            print("@@", y.id, y.name, [x.name for x in y.valid_xs], [[t.name for t in x.tags.all()] for x in y.valid_xs])
