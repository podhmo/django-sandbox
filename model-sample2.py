# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.db import models

"""hmm"""
from django.conf import settings
settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)


def get_connection():
    "get default database connection"
    from django.db import connections
    connection = connections['default']
    return connection


def get_cursor(connection):
    "get database cursor from connection"
    return connection.cursor()


def get_style():
    from django.core.management.color import no_style
    return no_style()


def create_table(model):
    connection = get_connection()
    cursor = get_cursor(connection)
    style = get_style()

    sql, references = connection.creation.sql_create_model(
        model, style)
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)


# model definition
class User(models.Model):
    name = models.CharField(max_length=255, null=False, default="")

    class Meta:
        app_label = "myapp"


class UserProfile(models.Model):
    score = models.IntegerField(null=False, default=0)
    user = models.OneToOneField(User, related_name="profile")

    class Meta:
        app_label = "myapp"


if __name__ == "__main__":
    import django
    django.setup()
    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    create_table(User)
    create_table(UserProfile)

    # NG
    # UserProfile(user=User()).save()
    # django.db.utils.IntegrityError: NOT NULL constraint failed: myapp_userprofile.user_id

    # NG
    # User(profile=UserProfile()).save()
    # TypeError: 'profile' is an invalid keyword argument for this function

    # OK
    user = User()
    user.save()
    UserProfile(user=user).save()
