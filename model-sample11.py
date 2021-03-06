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


class SubComment(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    comment = models.ForeignKey(Comment, null=False, related_name="subcomments")
    content = models.TextField(default="")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import logging

    create_table(Subject)
    create_table(Comment)
    create_table(SubComment)

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
    c = Comment(subject=subject, content="zzz")
    c.save()
    SubComment(comment=c, content="1").save()
    SubComment(comment=c, content="2").save()

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
    for s in Subject.objects.all().prefetch_related(
            Prefetch("comments", queryset=Comment.objects.all().defer("name"), to_attr="cs"),
            Prefetch("cs__subcomments", queryset=SubComment.objects.all().defer("name"), to_attr="scs")
    ).defer("name"):
        for c in s.cs:
            print(c.content)
            for sc in c.scs:
                print(sc.content)

    # qs = Subject.objects.all().prefetch_related("comments")
    # from django.db.models.query import normalize_prefetch_lookups
    # print(vars(normalize_prefetch_lookups(qs._prefetch_related_lookups)[0]))
    # print(vars(Prefetch("comments", queryset=Comment.objects.all().defer("name"), to_attr="cs")))
    print("-- deep nested ----------------------------------------")
    qs = Subject.objects.all().prefetch_related("comments", "comments__subcomments")
    qs = qs._clone()
    lookup = qs._prefetch_related_lookups[0]
    lookup2 = qs._prefetch_related_lookups[1]
    qs._prefetch_related_lookups = [
        Prefetch(lookup, queryset=Comment.objects.defer("name")),
        Prefetch(lookup2, queryset=SubComment.objects.defer("name")),
    ]
    for s in qs.defer("name"):
        for c in s.comments.all():
            print(c.content)
            for sc in c.subcomments.all():
                print(sc.content)
