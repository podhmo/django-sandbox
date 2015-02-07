# -*- coding:utf-8 -*-
"""
pip install factory_boy
"""

# prepare(see: model-sample.py)
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


def refresh_table(model):
    connection = get_connection()
    cursor = get_cursor(connection)
    style = get_style()

    sql = connection.creation.sql_destroy_model(
        model, [], style)
    for statement in sql:
        cursor.execute(statement)
    sql, references = connection.creation.sql_create_model(
        model, style)
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        refresh_table(f.rel.through)


########################################
# model
########################################
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255, default="", null=False)
    age = models.IntegerField(null=True)

    class Meta:
        app_label = "myapp"


class UserProfile(models.Model):
    score = models.IntegerField(default=0, null=False)
    user = models.OneToOneField(User, related_name="profile")
    # UserProfile().save() is NG. but User().save() is OK
    authority = models.ForeignKey("Authority")

    class Meta:
        app_label = "myapp"


class Authority(models.Model):
    is_paid = models.BooleanField(default=False, null=False)

    class Meta:
        app_label = "myapp"


########################################
# factories
########################################

import factory
from factory import fuzzy
import random
random.seed(1234)

marker = object()


class UserFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "foo{n}".format(n=n))
    age = fuzzy.FuzzyInteger(1, 30)

    class Meta:
        model = User


class UserProfileFactory(factory.DjangoModelFactory):
    score = fuzzy.FuzzyInteger(0, 1000)
    authority = factory.SubFactory("{}.AuthorityFactory".format(__name__))
    user = factory.SubFactory("{}.UserFactory".format(__name__))

    class Meta:
        model = UserProfile


class AuthorityFactory(factory.django.DjangoModelFactory):
    is_paid = False

    class Meta:
        model = Authority


########################################
# test
########################################
import unittest


class MultiRelationTests(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        refresh_table(User)
        refresh_table(UserProfile)
        refresh_table(Authority)
        logging.disable(logging.NOTSET)

    def describe(method):
        def wrapper(*args, **kwargs):
            print("----------------------------------------")
            print(method.__name__)
            print("----------------------------------------")
            return method(*args, **kwargs)
        return wrapper

    @describe
    def test_gen_profile(self):
        profile = UserProfileFactory()
        self.assertIsInstance(profile.user, User)
        self.assertEqual(profile.user.profile, profile)

    @describe
    def test_gen_profile2(self):
        profile = UserProfileFactory(user=UserFactory())
        self.assertIsInstance(profile.user, User)
        self.assertEqual(profile.user.profile, profile)

    @describe
    def test_gen_user(self):
        user = UserFactory()
        user.profile = UserProfileFactory(user=user)
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.user, user)

    @describe
    def test_gen_authority(self):
        profile = UserProfileFactory()
        user = profile.user
        self.assertIsInstance(user.profile.authority, Authority)
        self.assertFalse(user.profile.authority.is_paid)

    @describe
    def test_gen_authority2(self):
        profile = UserProfileFactory(authority__is_paid=True)
        user = profile.user
        self.assertIsInstance(user.profile.authority, Authority)
        self.assertTrue(user.profile.authority.is_paid)

    @describe
    def test_gen_authority3(self):
        profile = UserProfileFactory(authority=AuthorityFactory(is_paid=True))
        user = profile.user
        self.assertIsInstance(user.profile.authority, Authority)
        self.assertTrue(user.profile.authority.is_paid)


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
    create_table(Authority)
    unittest.main()
