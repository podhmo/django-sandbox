# -*- coding:utf-8 -*-

"""
proxy model and foreign keys
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


class Book(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    authors = models.ManyToManyField("Author", through='TitleAuthor')

    class Meta:
        db_table = "book"
        app_label = __name__


class Author(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)

    class Meta:
        db_table = "author"
        app_label = __name__


class TitleAuthor(models.Model):
    class Meta:
        db_table = "title_author"
        app_label = __name__
        unique_together = ("book", "author")

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)


class BookProxy(Book):
    class Meta:
        app_label = __name__
        proxy = True

    def hello(self):
        return "{}: hello".format(self.name)


class AuthorProxy(Author):
    class Meta:
        app_label = __name__
        proxy = True

    def hello(self):
        return "{}: hello".format(self.name)


class User(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    authors = models.ManyToManyField(Book, blank=True, through='UserAuthor')  # xxx

    class Meta:
        db_table = "user"
        app_label = __name__


class UserAuthor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # xxx

    class Meta:
        db_table = "user_author"
        unique_together = ('user', 'author')


class Booklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # xxx

    class Meta:
        db_table = "booklist"
        app_label = __name__


def setup():
    from django.apps import apps
    from collections import defaultdict
    coerce_map = defaultdict(list)
    for model in apps.get_models():
        if getattr(model._meta, "proxy", False):
            coerce_map[model._meta.concrete_model].append(model)

    # assertion
    for base_model, candidates in coerce_map.items():
        if len(candidates) > 1:
            msg = "coercing candidate is not unique: {} -> {}".format(base_model, candidates)
            raise AssertionError(msg)

    # monkey patch
    from django.db.models.query import ModelIterable
    original_method = ModelIterable.__iter__

    def iter_with_coercing(self):
        if hasattr(self.queryset.query, "model"):
            candidates = coerce_map[self.queryset.model]
            if candidates:
                self.queryset.query.model = candidates[0]
        yield from original_method(self)

    ModelIterable.__iter__ = iter_with_coercing

if __name__ == "__main__":
    create_table(User)
    create_table(Author)
    create_table(Book)
    create_table(TitleAuthor)
    create_table(UserAuthor)
    create_table(Booklist)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    User.objects.bulk_create([
        User(name="user0", id=1),
        User(name="user1", id=2),
        User(name="user2", id=3)
    ])
    BookProxy.objects.bulk_create([
        BookProxy(name="book0", id=10),
        BookProxy(name="book1", id=20),
        BookProxy(name="book2", id=30)
    ])
    # ValueError: "<BookProxy: BookProxy object>" needs to have a value for field "book" before this many-to-many relationship can be used.
    AuthorProxy.objects.bulk_create([
        AuthorProxy(name="author0", id=100),
        AuthorProxy(name="author1", id=200),
        AuthorProxy(name="author2", id=300)
    ])
    users = list(User.objects.all())
    authors = list(AuthorProxy.objects.all())
    books = list(BookProxy.objects.all())

    TitleAuthor.objects.bulk_create([
        TitleAuthor(book=books[0], author=authors[0]),
        TitleAuthor(book=books[0], author=authors[1]),
        TitleAuthor(book=books[1], author=authors[1]),
        TitleAuthor(book=books[2], author=authors[2]),
    ])
    UserAuthor.objects.bulk_create([
        UserAuthor(user=users[0], author=authors[0]),
        UserAuthor(user=users[1], author=authors[1]),
        UserAuthor(user=users[2], author=authors[2]),
    ])
    Booklist.objects.bulk_create([
        Booklist(user=users[0], book=books[0]),
        Booklist(user=users[0], book=books[1]),
        Booklist(user=users[0], book=books[2]),
    ])
    # def difference(xs, ys):
    #     return [set(xs).difference(ys), set(ys).difference(xs)]

    # print("---")
    # print("book proxy", BookProxy._meta.get_fields())
    # print("book", Book._meta.get_fields())
    # print("@difference book proxy - book", difference(BookProxy._meta.get_fields(), Book._meta.get_fields()))
    # print("user", User._meta.get_fields())
    # print("author proxy", AuthorProxy._meta.get_fields())
    # print("author", Author._meta.get_fields())
    # print("@difference author proxy - author", difference(AuthorProxy._meta.get_fields(), Author._meta.get_fields()))
    # print("---")

    print(books[0].authors.all())
    setup()
    print(books[0].authors.all())
    # # query
    # qs = Author.objects.filter(titleauthor__book__booklist__user=users[0])
    # authors = list(qs)
