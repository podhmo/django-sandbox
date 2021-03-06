# -*- coding:utf-8 -*-

"""
deep prefetch related with generic foreign key (more individual usecase)
"""
import threading
import contextlib
import django
from django.db import models
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
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class GFKPrefetchContext:
    def __init__(self):
        self._context = threading.local()
        self._context.attach_prefetch = lambda qs: qs

    @contextlib.contextmanager
    def activate_prefetch(self, fn):
        oldvalue = self._context.attach_prefetch
        self._context.attach_prefetch = fn
        yield
        self._context.attach_prefetch = oldvalue

    def attach_prefetch(self, qs):
        return self._context.attach_prefetch(qs)

gfk_prefetch_context = GFKPrefetchContext()


class ContentTypeWithPrefetch(ContentType):
    class Meta:
        proxy = True

    def get_all_objects_for_this_type(self, **kwargs):
        qs = super().get_all_objects_for_this_type(**kwargs)
        return gfk_prefetch_context.attach_prefetch(qs)


class MyGenericForeignKey(GenericForeignKey):
    def get_content_type(self, *args, **kwargs):
        ct = super().get_content_type(*args, **kwargs)
        ct.__class__ = ContentTypeWithPrefetch
        return ct


def create_table(model):
    connection = connections['default']
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class A(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "a"
        app_label = __name__


class B(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "b"
        app_label = __name__


class C(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "c"
        app_label = __name__


class X(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    a = models.ForeignKey(A, related_name="xs")

    class Meta:
        db_table = "x"
        app_label = __name__


class Y(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    b = models.ForeignKey(B, related_name="ys")

    class Meta:
        db_table = "y"
        app_label = __name__


class Feed(models.Model):
    class Meta:
        db_table = "feed"
        unique_together = ("content_type", "object_id")

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content = MyGenericForeignKey('content_type', 'object_id')


@contextlib.contextmanager
def with_clear_connection(c, message):
    print("\n========================================")
    print(message)
    print("========================================")
    c.queries_log.clear()
    yield


if __name__ == "__main__":
    create_table(A)
    create_table(B)
    create_table(C)
    create_table(X)
    create_table(Y)
    create_table(Feed)
    create_table(ContentType)

    A.objects.bulk_create([
        A(name="a0", id=1),
        A(name="a1", id=2),
        A(name="a2", id=3)
    ])
    B.objects.bulk_create([
        B(name="b0", id=10),
        B(name="b1", id=20),
        B(name="b2", id=30)
    ])
    C.objects.bulk_create([
        C(name="c0", id=100),
        C(name="c1", id=200),
        C(name="c2", id=300)
    ])
    a_list = list(A.objects.all())
    b_list = list(B.objects.all())
    c_list = list(C.objects.all())

    X.objects.bulk_create([
        X(name="x0a0", a=a_list[0]),
        X(name="x1a0", a=a_list[0]),
        X(name="x0a1", a=a_list[1]),
        X(name="x1a1", a=a_list[1]),
        X(name="x0a2", a=a_list[2]),
        X(name="x1a2", a=a_list[2]),
    ])
    Y.objects.bulk_create([
        Y(name="y0b0", b=b_list[0]),
        Y(name="y1b0", b=b_list[0]),
        Y(name="y0b1", b=b_list[1]),
        Y(name="y1b1", b=b_list[1]),
        Y(name="y0b2", b=b_list[2]),
        Y(name="y1b2", b=b_list[2]),
    ])
    Feed.objects.bulk_create(
        [Feed(content=a) for a in a_list]
        + [Feed(content=b) for b in b_list]
        + [Feed(content=c) for c in c_list]
    )

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    c = connections["default"]

    def use(content):
        if hasattr(content, "xs"):
            return [content, list(content.xs.all())]
        elif hasattr(content, "ys"):
            return [content, list(content.ys.all())]
        else:
            return [content]

    with with_clear_connection(c, "n + 1"):
        content_list = []
        for feed in Feed.objects.all():
            content_list.append(use(feed.content))
        print(len(c.queries))

    with with_clear_connection(c, "prefetch"):
        content_list = []
        for feed in Feed.objects.all().prefetch_related("content"):
            content_list.append(use(feed.content))
        print(len(c.queries))

    def attach_prefetch(qs):
        model = qs.model
        if issubclass(model, A):
            return qs.prefetch_related("xs")
        elif issubclass(model, B):
            return qs.prefetch_related("ys")
        else:
            return qs

    with with_clear_connection(c, "prefetch optimized"):
        content_list = []
        with gfk_prefetch_context.activate_prefetch(attach_prefetch):
            for feed in Feed.objects.all().prefetch_related("content"):
                content_list.append(use(feed.content))
            print(len(c.queries))
