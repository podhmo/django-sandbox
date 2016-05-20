# -*- coding:utf-8 -*-

"""
prefetch related with defer.
prefetch with defer (simply style) is not active. (n + 1 queries are occured)
"""
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


class Subject(models.Model):
    name = models.CharField(max_length=32, default="foo", blank=False)

    class Meta:
        app_label = __name__


class Comment(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    subject = models.ForeignKey(Subject, null=False, related_name="comments")
    content = models.TextField(default="")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import logging

    create_table(Subject)
    create_table(Comment)

    subject = Subject(name="X")
    subject.save()
    Comment(subject=subject, content="x").save()
    Comment(subject=subject, content="xx").save()

    subject = Subject(name="Y")
    subject.save()
    Comment(subject=subject, content="y").save()

    subject = Subject(name="Z")
    subject.save()
    Comment(subject=subject, content="z").save()
    Comment(subject=subject, content="zz").save()
    Comment(subject=subject, content="zzz").save()

    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    for s in Subject.objects.all():
        for c in s.comments.all():
            print(c.content)
    print("==prefetch ======================================")
    for s in Subject.objects.all().prefetch_related("comments"):
        for c in s.comments.all():
            print(c.content)
    print("==prefetch with defer ======================================")
    for s in Subject.objects.all().prefetch_related("comments").defer("name"):
        for c in s.comments.all().defer("name"):
            print(c.content)

    from django.db.models import Prefetch
    print("==Prefetch with defer ======================================")
    for s in Subject.objects.all().prefetch_related(Prefetch("comments", queryset=Comment.objects.all().defer("name"), to_attr="cs")).defer("name"):
        for c in s.cs:
            print(c.content)
