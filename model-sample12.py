# -*- coding:utf-8 -*-

"""
select related
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

    class Meta:
        app_label = __name__


class UserKarma(models.Model):
    user = models.OneToOneField(User, related_name="karma")
    point = models.IntegerField(null=False, default=0)

    class Meta:
        app_label = __name__


class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments")
    content = models.CharField(max_length=140, null=False, default="")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    create_table(User)
    create_table(UserKarma)
    create_table(Comment)

    user = User(name="foo")
    user.save()
    karma = UserKarma(user=user, point=10)
    karma.save()
    Comment(user=user, content="*").save()
    Comment(user=user, content="*").save()
    Comment(user=user, content="*").save()

    user = User(name="bar")
    user.save()
    karma = UserKarma(user=user, point=20)
    karma.save()
    Comment(user=user, content="*").save()

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    print("----------------------------------------")
    print(User.objects.select_related("karma").query)
    for u in User.objects.select_related("karma"):
        print(u.name, u.karma.point)
    print("----------------------------------------")
    print(UserKarma.objects.select_related("user").query)
    for k in UserKarma.objects.select_related("user"):
        print(k.user.name, k.point)
    print("----------------------------------------")
    print(Comment.objects.select_related("user").query)
    # print(User.objects.select_related("comments").query)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for u in User.objects.prefetch_related("comments"):
        # print(u._prefetched_objects_cache)
        print(u.name, [c.content for c in u.comments.all()])
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for u in User.objects.prefetch_related("comments").defer("name"):
        print(u.name, [c.content for c in u.comments.all().defer("id")])

    qs = User.objects.prefetch_related("comments")
