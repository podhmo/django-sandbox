# -*- coding:utf-8 -*-

"""
prefetch related for custom child query with filter condition
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
    memo = models.TextField(null=True)

    class Meta:
        app_label = __name__


class Skill(models.Model):
    user = models.ForeignKey(User, related_name="skills")
    name = models.CharField(max_length=32, default="X", blank=False)
    memo = models.TextField(null=True)

    class Meta:
        app_label = __name__


class Group(models.Model):
    users = models.ManyToManyField(User, related_name="groups")
    name = models.CharField(max_length=32, default="foo", blank=False)
    memo = models.TextField(null=True)

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    create_table(User)
    create_table(Skill)
    create_table(Group)

    user = User(name="foo")
    user.save()
    skill = Skill(name="x", user=user)
    skill.save()
    skill = Skill(name="y", user=user)
    skill.save()
    user1 = User(name="bar")
    user1.save()
    skill = Skill(name="x", user=user1)
    skill.save()
    group = Group(name="A")
    group.save()
    group.users.add(user)
    group.users.add(user1)

    group1 = Group(name="B")
    group.save()
    group.users.add(user)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    from django.db.models import Prefetch
    for g in Group.objects.prefetch_related(
            Prefetch("users", queryset=User.objects.filter(id__lt=10))
    ):
        print(g.name, [u.name for u in g.users.all()])

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for g in Group.objects.only("name").prefetch_related(
            Prefetch("users", queryset=User.objects.filter(id__lt=10).only("name")),
            Prefetch("users__skills", queryset=Skill.objects.filter(id__lt=9).only("name", "user_id"))
    ):
        print(g.name)
        for u in g.users.all():
            print("\t", u.name)
            for s in u.skills.all():
                print("\t\t", s.name)

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    for g in Group.objects.defer("memo").prefetch_related(
            Prefetch("users", queryset=User.objects.filter(id__lt=10).defer("memo")),
            Prefetch("users__skills", queryset=Skill.objects.filter(id__lt=9).defer("memo"))
    ):
        print(g.name)
        for u in g.users.all():
            print("\t", u.name)
            for s in u.skills.all():
                print("\t\t", s.name)
    # print(Group._meta.get_field("users").attname)
    # print(User._meta.get_field("skills").attname)
