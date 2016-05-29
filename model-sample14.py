# -*- coding:utf-8 -*-

"""
select related with only
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


class User(models.Model):
    name = models.CharField(max_length=32, default="foo", blank=False)
    ctime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__


class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments")
    content = models.CharField(max_length=140, null=False, default="")
    ctime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    create_table(User)
    create_table(Comment)

    user = User(name="foo")
    user.save()
    Comment(user=user, content="*").save()
    Comment(user=user, content="*").save()

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    for c in Comment.objects.select_related("user"):
        print("\t\t", c.user.name, c.content)

    for c in Comment.objects.select_related("user").only("content", "user__name"):
        print("\t\t", c.user.name, c.content)
