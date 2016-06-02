# -*- coding:utf-8 -*-

"""
aggressive query with count
need: pip install django-aggressivequery
"""
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
    INSTALLED_APPS=[__name__]
)
django.setup()


def create_table(model):
    connection = connections['default']
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class A(models.Model):
    name = models.CharField(max_length=32, default="a", blank=False)
    ctime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__


class B(models.Model):
    a = models.ForeignKey(A, related_name="children")
    name = models.CharField(max_length=140, null=False, default="")
    ctime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__


class C(models.Model):
    b = models.ForeignKey(B, related_name="children")
    name = models.CharField(max_length=140, null=False, default="")
    ctime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    create_table(A)
    create_table(B)
    create_table(C)

    a0 = A.objects.create(name="a0")
    b0 = B.objects.create(name="b00", a=a0)
    b1 = B.objects.create(name="b01", a=a0)
    b2 = B.objects.create(name="b02", a=a0)
    C.objects.create(name="c000", b=b0)
    C.objects.create(name="c001", b=b0)
    C.objects.create(name="c002", b=b0)
    C.objects.create(name="c010", b=b1)
    C.objects.create(name="c011", b=b1)
    C.objects.create(name="c012", b=b1)
    C.objects.create(name="c020", b=b2)
    C.objects.create(name="c021", b=b2)
    C.objects.create(name="c022", b=b2)
    a1 = A.objects.create(name="a1")
    b0 = B.objects.create(name="b10", a=a1)
    b1 = B.objects.create(name="b11", a=a1)
    b2 = B.objects.create(name="b12", a=a1)
    C.objects.create(name="c100", b=b0)
    C.objects.create(name="c101", b=b0)
    C.objects.create(name="c102", b=b0)
    C.objects.create(name="c110", b=b1)
    C.objects.create(name="c111", b=b1)
    C.objects.create(name="c112", b=b1)
    C.objects.create(name="c120", b=b2)
    C.objects.create(name="c121", b=b2)
    C.objects.create(name="c122", b=b2)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    from django.db.models import Count
    qs = A.objects.annotate(c=Count('children__a_id'))
    for a in qs:
        print(a.name, a.c)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    from django_aggressivequery import from_query as aggressive_query

    qs = A.objects.annotate(c=Count('children__a_id'))
    qs = (aggressive_query(qs, ["children__children"])
          .prefetch_filter(children=lambda qs: qs.annotate(c=Count('children__b_id'))))
    for a in qs:
        for b in a.children.all():
            for c in b.children.all():
                print(a.name, a.c, b.name, b.c, c.name)
