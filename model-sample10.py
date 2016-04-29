# -*- coding:utf-8 -*-

"""
ordering by joined count
"""

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


class Subject(models.Model):
    name = models.CharField(max_length=32, default="foo", blank=False)

    class Meta:
        app_label = __name__


class Comment(models.Model):
    subject = models.ForeignKey(Subject, null=False)
    content = models.TextField(default="")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

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

    qs = Subject.objects.annotate(c=models.Count('comment__subject_id')).order_by("-c")
    for subject in qs:
        print(subject.name, subject.c)

    """
    SELECT subject.id, subject.name, COUNT(comment.subject_id) AS c
    FROM subject LEFT OUTER JOIN comment ON ( subject.id = comment.subject_id )
    GROUP BY subject.id, subject.name
    ORDER BY c DESC
    """
