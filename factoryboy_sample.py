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
import random
random.seed(1234)


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User

    name = factory.Sequence(lambda n: "foo{n}".format(n=n))
    age = factory.LazyAttribute(lambda x: int(30 * random.random()))

    @factory.post_generation
    def profile(obj, create, extracted, **kwargs):
        if extracted:
            extracted.user = obj
            return extracted
        return UserProfileFactory.create(user=obj)


class UserProfileFactory(factory.Factory):
    FACTORY_FOR = UserProfile

    authority = factory.LazyAttribute(lambda x: AuthorityFactory())
    score = factory.LazyAttribute(lambda x: int(1000 * random.random()))

    @factory.post_generation
    def user(obj, create, extracted, **kwargs):
        if extracted:
            extracted.profile = obj
            return extracted
        return UserFactory.create(profile=obj)


class AuthorityFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Authority

    is_paid = False


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
        profile.save()
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
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.user, user)

    @describe
    def test_gen_user2(self):
        user = UserFactory(profile=UserProfileFactory())
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.user, user)

    @describe
    def test_gen_authority(self):
        user = UserFactory()
        self.assertIsInstance(user.profile.authority, Authority)
        self.assertFalse(user.profile.authority.is_paid)

    @describe
    def test_gen_authority2(self):
        user = UserFactory(profile=UserProfileFactory(authority=AuthorityFactory(is_paid=True)))
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
