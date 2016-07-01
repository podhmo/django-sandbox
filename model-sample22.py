# -*- coding:utf-8 -*-

"""
prefetch related with aggregated values
"""
import django
import contextlib
from django.db import models
from django.conf import settings
from django.db import connections
from django.db.models import Count


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__, "django.contrib.contenttypes"]
)
django.setup()


def create_table(model):
    connection = connections['default']
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class AggregatedPrefetcher(object):
    def __init__(self, name, cache_name, gen_query):
        self.name = name
        self.cache_name = cache_name
        self.gen_query = gen_query

    def is_cached(self, instance):
        return False

    def get_prefetch_queryset(self, objs, qs):
        if qs is not None:
            raise ValueError("Aggregated queryset can't be used for this lookup.")

        id_list = [o.id for o in objs]
        result = list(self.gen_query(objs, self.name).filter(id__in=id_list))
        single = True
        return (
            result,
            self.key_from_rel_obj,
            self.key_from_instance,
            single,
            self.cache_name
        )

    def key_from_rel_obj(self, relobj):
        return relobj["id"]

    def key_from_instance(self, obj):
        return obj.id


class AggregatedPrefetchDescriptor(object):
    def __init__(self, name, gen_query):
        cache_name = "_{}_dict".format(name)
        self.prefetcher = AggregatedPrefetcher(name, cache_name, gen_query)

    def __get__(self, ob, type_=None):
        if ob is None:
            return self.prefetcher
        elif hasattr(ob, self.prefetcher.cache_name):
            return getattr(ob, self.prefetcher.cache_name)[self.prefetcher.name]
        else:
            d = {"id": ob.id, self.prefetcher.name: Comment.objects.filter(post=ob).count()}
            setattr(ob, self.prefetcher.cache_name, d)
            return d[self.prefetcher.name]


@contextlib.contextmanager
def with_clear_connection(c, message):
    print("\n========================================")
    print(message)
    print("========================================")
    c.queries_log.clear()
    yield


class Post(models.Model):
    name = models.CharField(max_length=32, default="", blank=False)
    content = models.TextField(default="", blank=False)

    def comment_count_query(objs, name):
        return Post.objects.values("id").annotate(**{name: Count('comment__post_id')})

    comment_count = AggregatedPrefetchDescriptor("comment_count", comment_count_query)

    class Meta:
        db_table = "post"
        app_label = __name__


class Comment(models.Model):
    post = models.ForeignKey(Post)
    content = models.CharField(max_length=255, default="", blank=False)
    # todo: user

    class Meta:
        db_table = "comment"
        app_label = __name__


if __name__ == "__main__":
    create_table(Post)
    create_table(Comment)

    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    Post.objects.bulk_create([
        Post(name="a0"),
        Post(name="a1"),
        Post(name="a2")
    ])
    posts = list(Post.objects.all())
    Comment.objects.bulk_create([
        Comment(content="foo", post=posts[0]),
        Comment(content="bar", post=posts[0]),
        Comment(content="boo", post=posts[0]),
        Comment(content="xxx", post=posts[1]),
        Comment(content="yyy", post=posts[1]),
        Comment(content="@@@", post=posts[2]),
    ])

    qs = Post.objects.values("id").annotate(c=Count('comment__post_id'))
    print(qs)

    c = connections["default"]
    with with_clear_connection(c, "n + 1"):
        print(len(c.queries))
        comment_count_list = []
        for post in Post.objects.all():
            comment_count_list.append((post.id, post.comment_count))
        print(len(c.queries))  # => 1 + 3 * 1 = 4
        print(comment_count_list)

    with with_clear_connection(c, "prefetch"):
        print(len(c.queries))
        comment_count_list = []
        qs = Post.objects.all().prefetch_related("comment_count")
        for post in qs:
            comment_count_list.append((post.id, post.comment_count))
        print(len(c.queries))  # => 1 + 1 = 2
        print(comment_count_list)
